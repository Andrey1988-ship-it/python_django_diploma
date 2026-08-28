from celery import shared_task
from django.shortcuts import get_object_or_404
# Импортируем модель заказа из нового разделенного приложения orders
from orders.models import Order

@shared_task
def process_order_payment(order_id, account_number):
    """
    Фоновая асинхронная задача Celery для имитации оплаты по ТЗ (Страница 6).
    Логика:
    - Если номер четный и не заканчивается на 0 -> Оплачено.
    - Иначе -> Ошибка оплаты со случайным кодом.
    """
    import random
    print(f"⏳ Celery начал обработку платежа для заказа №{order_id}...")

    # Находим заказ в базе данных
    order = Order.objects.get(id=order_id)

    try:
        # Проверяем условия по ТЗ
        if account_number.isdigit():
            num = int(account_number)
            if num % 2 == 0 and not account_number.endswith('0'):
                # Успешный платеж
                order.status = 'Оплачено'
                order.payment_error = None
                print(f"✅ Заказ №{order_id} успешно оплачен счетом {account_number}")
            else:
                # Ошибка валидации номера по ТЗ
                order.status = 'Ошибка оплаты'
                errors = [
                    "Платёжная система отклонила операцию: счёт оканчивается на ноль.",
                    "Ошибка транзакции: указан нечётный номер счёта/карты.",
                    "Недостаточно средств на случайном чужом счёте.",
                    "Платёжный шлюз временно недоступен. Попробуйте позже."
                ]
                order.payment_error = random.choice(errors)
                print(f"❌ Ошибка оплаты заказа №{order_id}: {order.payment_error}")
        else:
            order.status = 'Ошибка оплаты'
            order.payment_error = "Некорректный формат номера счёта (содержит не только цифры)."

    except Exception as e:
        order.status = 'Ошибка оплаты'
        order.payment_error = f"Системный сбой платёжной системы: {str(e)}"

    # Сохраняем обновленный статус и текст ошибки в базу
    order.save()
