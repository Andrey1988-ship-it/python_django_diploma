import os
from django.db import models
from django.contrib.auth.models import User
from PIL import Image

# --- Исправленный Механизм Мягкого Удаления (Soft Delete) ---
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
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


# --- Модели каталога ---
class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название тега")

    def __str__(self):
        return self.name


class Category(SoftDeleteModel):
    title = models.CharField(max_length=255, verbose_name="Название категории")
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

    def delete(self, *args, **kwargs):
        """Мягкое удаление объекта: вместо удаления меняем флаг"""
        self.is_deleted = True
        self.save()


    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Товар")
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="Автор")
    text = models.TextField(verbose_name="Текст отзыва")
    rate = models.PositiveSmallIntegerField(verbose_name="Оценка (1-5)")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Отзыв от {self.author.username} на {self.product.name}"


class ProductImage(models.Model):
    """Изображения товара для галереи по ТЗ"""
    # Использованы кавычки 'Product', чтобы избежать NameError, если класс сместится
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images', verbose_name="Товар")
    image = models.ImageField(upload_to='products/', verbose_name="Файл изображения")
    alt = models.CharField(max_length=255, blank=True, verbose_name="Альтернативный текст (alt)")

    def __str__(self):
        return f"Картинка для {self.product.name if self.product else 'Удаленного товара'}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            max_size = (400, 400)
            if img.height > 400 or img.width > 400:
                img.thumbnail(max_size)
                img.save(self.image.path)
