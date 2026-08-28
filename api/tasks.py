import random
from celery import shared_task
from .models import Order


@shared_task
def process_order_payment(order_id, account_number):
    """Фоновая задача Celery для симуляции задержки банка и оплаты по ТЗ"""
    try:
        order = Order.objects.get(id=order_id)

        # Симулируем задержку ответа банковского сервера (например, 3 секунды)
        import time
        time.sleep(3)

        # Если фронтенд прислал пустой номер, генерируем случайный
        if not account_number:
            account_number = str(random.randint(10000002, 99999998))

        # Строгая бизнес-логика проверки из ТЗ: чётный и не на ноль
        if int(account_number) % 2 == 0 and not account_number.endswith('0'):
            order.status = 'Оплачено'
            order.payment_error = None
            print(f"💳 [CELERY] Заказ №{order.id} успешно оплачен через фоновую задачу!")
        else:
            order.status = 'Ошибка оплаты'
            order.payment_error = 'Номер нечетный или заканчивается на ноль (Фоновый сбой эквайринга)'
            print(f"❌ [CELERY] Сбой фоновой оплаты заказа №{order.id}")

        order.save()
        return f"Order {order_id} processed with status: {order.status}"

    except Order.DoesNotExist:
        return f"Order {order_id} not found"
