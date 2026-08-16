from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Импортируем модель заказа из соседнего приложения orders
from orders.models import Order
# Импортируем асинхронную задачу Celery из текущего приложения payment
from .tasks import process_order_payment


class PaymentView(APIView):
    """Имитация банковского эквайринга через фоновые задачи Celery по ТЗ"""

    def post(self, request, id):
        user = request.user
        if not user or not user.is_authenticated:
            user = User.objects.order_by('id').first()

        order = get_object_or_404(Order, id=id, user=user)
        raw_number = str(request.data.get('number', ''))
        account_number = "".join(filter(str.isdigit, raw_number))

        # Переводим статус заказа в "Ожидает оплаты"
        order.status = 'Ожидает оплаты'
        order.save()

        # ОТПРАВЛЯЕМ ЗАДАЧУ В ОЧЕРЕДЬ CELERY АСИНХРОННО через .delay()
        process_order_payment.delay(order.id, account_number)

        print(f"🚀 Заказ №{order.id} отправлен в фоновую очередь Celery на оплату счетом {account_number}")

        # Мгновенно возвращаем ответ фронтенду, как требует спецификация асинхронного API
        return Response(status=status.HTTP_200_OK)
