from django.db import models
from django.db import models
from django.contrib.auth.models import User
# Импортируем товар и абстрактную модель мягкого удаления из приложения products
from products.models import  SoftDeleteModel

class Order(SoftDeleteModel):
    STATUS_CHOICES = [
        ('Ожидает оплаты', 'Ожидает оплаты'),
        ('Оплачено', 'Оплачено'),
        ('Ошибка оплаты', 'Ошибка оплаты'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Покупатель")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    delivery_type = models.CharField(max_length=50, default='Обычная', verbose_name="Способ доставки")
    payment_type = models.CharField(max_length=50, default='Онлайн картой', verbose_name="Способ оплаты")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Общая стоимость")

    city = models.CharField(max_length=255, null=True, blank=True, verbose_name="Город")
    address = models.TextField(null=True, blank=True, verbose_name="Адрес доставки")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к заказу")

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Ожидает оплаты', verbose_name="Статус заказа")
    payment_error = models.TextField(null=True, blank=True, verbose_name="Текст ошибки оплаты")

    def __str__(self):
        return f"Заказ №{self.id} ({self.user.username})"


class OrderItem(models.Model):
    """Состав заказа: конкретный товар, его количество и цена на момент покупки"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, verbose_name="Товар")

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена при покупке")
    count = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return f"{self.product.name if self.product else 'Удаленный товар'} x {self.count}"


