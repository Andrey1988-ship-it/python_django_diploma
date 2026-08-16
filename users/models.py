from django.db import models
import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
# Импортируем абстрактную модель мягкого удаления из приложения products
from products.models import SoftDeleteModel

def validate_avatar_size(fieldfile_obj):
    """Валидатор размера аватарки по ТЗ (максимум 2 Мб)"""
    filesize = fieldfile_obj.file.size
    megabyte_limit = 2.0
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(
            f"Максимальный размер аватарки — {megabyte_limit} Мб. "
            f"Ваш файл: {round(filesize / (1024*1024), 2)} Мб."
        )


class Profile(SoftDeleteModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Покупатель")
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, validators=[validate_avatar_size], verbose_name="Аватарка")

    def __str__(self):
        return self.user.username

    # Метод автоматического центрирования и сжатия аватарки
    def save(self, *args, **kwargs):
        # 1. Сначала сохраняем оригинальный файл на жесткий диск
        super().save(*args, **kwargs)

        if self.avatar and os.path.exists(self.avatar.path):
            # 2. Открываем изображение через Pillow
            img = Image.open(self.avatar.path)

            # Уменьшаем картинку до аккуратных размеров
            avatar_size = (200, 200)
            img.thumbnail(avatar_size, Image.Resampling.LANCZOS)

            # 3. Создаем прозрачный холст (RGBA) 1000х1000 под требования фронтенда
            canvas_size = (1000, 1000)
            canvas = Image.new('RGBA', canvas_size, (255, 255, 255, 0))

            # 4. Вычисляем координаты, чтобы вставить фото строго по центру
            x = (canvas_size[0] - img.width) // 2
            y = (canvas_size[1] - img.height) // 2

            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            canvas.paste(img, (x, y), img)

            # 5. Принудительно сохраняем в PNG для поддержки прозрачности пикселей
            orig_path = self.avatar.path
            base_path, _ = os.path.splitext(orig_path)
            new_path = base_path + ".png"

            canvas.save(new_path, 'PNG')

            # Корректируем имя файла в базе данных, если расширение изменилось
            if orig_path != new_path:
                if os.path.exists(orig_path):
                    os.remove(orig_path)
                self.avatar.name = os.path.relpath(new_path, start=settings.MEDIA_ROOT)
                super().save(update_fields=['avatar'])

