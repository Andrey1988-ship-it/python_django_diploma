import json
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser

from orders.models import Order
from .tasks import process_order_payment


class PaymentView(APIView):
    parser_classes = (JSONParser, FormParser)
    """Имитация банковского эквайринга через фоновые задачи Celery по ТЗ"""

    def post(self, request, id):
        user = request.user
        if not user or not user.is_authenticated:
            user = User.objects.order_by('id').first()
        if not user:
            return Response({"error": "В системе нет пользователей"}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, id=id, user=user)

        # ФИКС: парсим "капризные" данные от Megano
        data = request.data
        if isinstance(data, dict) and len(data) == 1:
            key = list(data.keys())[0]
            if key.startswith('{'):
                try:
                    data = json.loads(key)
                except json.JSONDecodeError:
                    pass
        if not isinstance(data, dict):
            try:
                data = json.loads(request.body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        raw_number = str(data.get('number', ''))
        account_number = "".join(filter(str.isdigit, raw_number))

        order.status = 'Ожидает оплаты'
        order.save()

        # ФИКС: оборачиваем вызов Celery в try-except, чтобы не было 500, если Redis не запущен
        try:
            process_order_payment.delay(order.id, account_number)
        except Exception as e:
            print(f"⚠️ Celery/Redis не запущены, ошибка: {e}")
            # Если Celery недоступен, обрабатываем синхронно (fallback)
            process_order_payment(order.id, account_number)

        return Response(status=status.HTTP_200_OK)