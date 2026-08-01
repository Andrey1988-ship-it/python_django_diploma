from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.exceptions import ValidationError
# --- Механизм Мягкого Удаления (Soft Delete) по ТЗ ---
from django.db import models
from django.contrib.auth.models import User
from PIL import Image


# --- Исправленный Механизм Мягкого Удаления (Soft Delete) ---
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # Используем стандартный метод базового класса, чтобы избежать рекурсии
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, verbose_name="Удален (мягкое удаление)")

    objects = SoftDeleteManager()  # Показывает только активные объекты
    all_objects = models.Manager()  # Показывает все объекты (включая удаленные)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()


# --- Остальные модели (Tag, Category, Product, Review) остаются без изменений ---


# --- Модели Интернет-Магазина ---

class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название тега")

    def __str__(self):
        return self.name


class Category(SoftDeleteModel):
    title = models.CharField(max_length=255, verbose_name="Название категории")
    # Вложенность категорий (макс. 2 уровня по ТЗ)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='subcategories', verbose_name="Родительская категория"
    )
    image_src = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name="Иконка/Картинка")
    image_alt = models.CharField(max_length=255, blank=True, verbose_name="Описание картинки")

    def __str__(self):
        return self.title


class Product(SoftDeleteModel):
    name = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(blank=True, verbose_name="Краткое описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    count = models.PositiveIntegerField(default=0, verbose_name="Количество в наличии")
    sort_index = models.IntegerField(default=0, verbose_name="Индекс сортировки")
    sales_count = models.PositiveIntegerField(default=0, verbose_name="Количество покупок")
    limited_edition = models.BooleanField(default=False, verbose_name="Ограниченный тираж")
    free_delivery = models.BooleanField(default=False, verbose_name="Бесплатная доставка")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    tags = models.ManyToManyField(Tag, blank=True, related_name='products', verbose_name="Теги")

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Товар")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    text = models.TextField(verbose_name="Текст отзыва")
    rate = models.PositiveSmallIntegerField(verbose_name="Оценка (1-5)")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Отзыв от {self.author.username} на {self.product.name}"

def validate_avatar_size(fieldfile_obj):
    """Валидатор размера аватарки по ТЗ (максимум 2 Мб)"""
    filesize = fieldfile_obj.file.size
    megabyte_limit = 2.0
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"Максимальный размер аватарки — {megabyte_limit} Мб. Ваш файл: {round(filesize / (1024*1024), 2)} Мб.")

class Profile(SoftDeleteModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Покупатель")
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Телефон")
    # Добавляем валидатор размера файла по ТЗ сюда:
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, validators=[validate_avatar_size], verbose_name="Аватарка")

    def __str__(self):
        return self.user.username

    class Profile(SoftDeleteModel):
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Покупатель")
        phone = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Телефон")
        avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, validators=[validate_avatar_size],
                                   verbose_name="Аватарка")

        def __str__(self):
            return self.user.username

        # ДОБАВЛЯЕМ МЕТОД АВТО-СЖАТИЯ АВАТАРКИ:
        def save(self, *args, **kwargs):
            # 1. Сначала сохраняем файл на диск
            super().save(*args, **kwargs)

            if self.avatar and os.path.exists(self.avatar.path):
                # 2. Открываем оригинального окуня
                img = Image.open(self.avatar.path)

                # Уменьшаем окуня до нужного аккуратного размера
                avatar_size = (200, 200)
                img.thumbnail(avatar_size, Image.Resampling.LANCZOS)

                # 3. Создаем огромный полностью прозрачный холст (RGBA)
                # Фронтенд растянет его, но прозрачные пиксели будут невидимы
                canvas_size = (1000, 1000)
                canvas = Image.new('RGBA', canvas_size, (255, 255, 255, 0))

                # 4. Вычисляем координаты центра, чтобы вставить окуня строго посередине
                x = (canvas_size[0] - img.width) // 2
                y = (canvas_size[1] - img.height) // 2

                # Если оригинальная картинка была без альфа-канала (JPG), конвертируем в RGBA
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                canvas.paste(img, (x, y), img)

                # 5. Принудительно меняем расширение файла на .png (чтобы работала прозрачность)
                # и перезаписываем аватарку
                orig_path = self.avatar.path
                base_path, _ = os.path.splitext(orig_path)
                new_path = base_path + ".png"

                canvas.save(new_path, 'PNG')

                # Корректируем имя файла в БД, если оно изменилось с .jpg на .png
                if orig_path != new_path:
                    if os.path.exists(orig_path):
                        os.remove(orig_path)
                    self.avatar.name = os.path.relpath(new_path, start=settings.MEDIA_ROOT)
                    super().save(update_fields=['avatar'])


class Order(SoftDeleteModel):
    # Варианты статусов по ТЗ
    STATUS_CHOICES = [
        ('Ожидает оплаты', 'Ожидает оплаты'),
        ('Оплачено', 'Оплачено'),
        ('Ошибка оплаты', 'Ошибка оплаты'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Покупатель")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    # Параметры пользователя и доставки (заполняются пошагово на форме оформления)
    delivery_type = models.CharField(max_length=50, default='Обычная', verbose_name="Способ доставки")
    payment_type = models.CharField(max_length=50, default='Онлайн картой', verbose_name="Способ оплаты")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Общая стоимость")

    city = models.CharField(max_length=255, null=True, blank=True, verbose_name="Город")
    address = models.TextField(null=True, blank=True, verbose_name="Адрес доставки")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к заказу")

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Ожидает оплаты',
                              verbose_name="Статус заказа")
    payment_error = models.TextField(null=True, blank=True, verbose_name="Текст ошибки оплаты")

    def __str__(self):
        return f"Заказ №{self.id} ({self.user.username})"


class OrderItem(models.Model):
    """Состав заказа: конкретный товар, его количество и цена на момент покупки"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="Товар")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена при покупке")
    count = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return f"{self.product.name if self.product else 'Удаленный товар'} x {self.count}"

class ProductImage(models.Model):
    """Изображения товара для галереи по ТЗ"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Товар")
    image = models.ImageField(upload_to='products/', verbose_name="Файл изображения")
    alt = models.CharField(max_length=255, blank=True, verbose_name="Альтернативный текст (alt)")

    def __str__(self):
        return f"Картинка для {self.product.name}"

    def save(self, *args, **kwargs):
        # Сначала сохраняем файл в оригинальном размере, чтобы он лег на диск
        super().save(*args, **kwargs)

        if self.image:
            # Открываем загруженную картинку через Pillow
            img = Image.open(self.image.path)

            # Задаем максимальный размер, который будет красиво смотреться на сайте
            max_size = (400, 400)

            # Если картинка больше этого размера — сжимаем её с сохранением пропорций
            if img.height > 400 or img.width > 400:
                img.thumbnail(max_size)
                # Перезаписываем файл на диске уменьшенной копией
                img.save(self.image.path)
