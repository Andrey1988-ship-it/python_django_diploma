from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Импортируем товары из products, а заказы из текущего приложения
from products.models import Product
from products.serializers import ProductSerializer
from .models import Order, OrderItem


class BasketView(APIView):
    """Изолированная сессионная корзина гостей и покупателей"""

    def get_basket(self, request):
        if 'basket' not in request.session:
            request.session['basket'] = {}
        return request.session['basket']

    def format_basket_response(self, basket_data):
        response_data = []
        for product_id, count in list(basket_data.items()):
            if not product_id or product_id in ['None', 'null']:
                continue
            try:
                product = Product.objects.get(id=int(product_id), is_deleted=False)
                product_json = ProductSerializer(product, context={'request': self.request}).data
                product_json['count'] = count
                response_data.append(product_json)
            except (Product.DoesNotExist, ValueError):
                if product_id in basket_data:
                    del basket_data[product_id]
                continue
        return response_data

    def get(self, request):
        return Response(self.format_basket_response(self.get_basket(request)))

    def post(self, request):
        basket = self.get_basket(request)
        product_id = request.data.get('id') or request.query_params.get('id')
        count = request.data.get('count') or request.query_params.get('count') or 1
        if product_id and str(product_id).isdigit():
            p_id_str = str(product_id)
            basket[p_id_str] = basket.get(p_id_str, 0) + int(count)
            request.session.modified = True
        return Response(self.format_basket_response(basket))

    def delete(self, request):
        basket = self.get_basket(request)
        product_id = request.data.get('id') or request.query_params.get('id')
        count = request.data.get('count') or request.query_params.get('count') or 1
        if product_id and str(product_id) in basket:
            p_id_str = str(product_id)
            if basket[p_id_str] > int(count):
                basket[p_id_str] -= int(count)
            else:
                del basket[p_id_str]
            request.session.modified = True
        return Response(self.format_basket_response(basket))


class OrdersView(APIView):
    """Сборка товаров из сессионной корзины в черновик заказа"""

    def post(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            user = User.objects.order_by('id').first()
        if not user:
            return Response({"error": "В системе нет пользователей"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        basket = request.session.get('basket', {})
        if not basket and isinstance(request.data, list):
            basket = {str(item.get('id')): item.get('count', 1) for item in request.data if item.get('id')}
        if not basket:
            return Response({"error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=user)
        total_cost = 0
        for product_id, count in basket.items():
            if not product_id or product_id in ['None', 'null']:
                continue
            try:
                product = Product.objects.get(id=int(product_id), is_deleted=False)
                OrderItem.objects.create(order=order, product=product, price=product.price, count=int(count))
                total_cost += product.price * int(count)
            except (Product.DoesNotExist, ValueError):
                continue

        order.total_cost = total_cost
        order.save()
        request.session['basket'] = {}
        request.session.modified = True
        return Response({"orderId": order.id}, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    """Пошаговое заполнение адреса доставки и расчет стоимости по правилам ТЗ"""

    def get_current_user(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            user = User.objects.order_by('id').first()
        return user

    def get(self, request, id):
        current_user = self.get_current_user(request)
        if not current_user:
            return Response({"error": "Пользователи не найдены"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        order = get_object_or_404(Order, id=id, user=current_user)
        items_data = []
        for item in order.items.all():
            if item.product:
                p_data = ProductSerializer(item.product, context={'request': request}).data
                p_data['count'] = item.count
                p_data['price'] = str(item.price)
                items_data.append(p_data)

        return Response({
            "id": order.id,
            "createdAt": order.date_created.strftime('%Y-%m-%d %H:%M'),
            "fullName": current_user.first_name or current_user.username,
            "email": current_user.email or "email@example.com",
            "phone": getattr(current_user, 'profile', None).phone if hasattr(current_user, 'profile') and current_user.profile else "",
            "deliveryType": order.delivery_type,
            "paymentType": order.payment_type,
            "totalCost": str(order.total_cost),
            "status": order.status,
            "city": order.city or "",
            "address": order.address or "",
            "products": items_data
        })

    def post(self, request, id):
        current_user = self.get_current_user(request)
        order = get_object_or_404(Order, id=id, user=current_user)
        order.city = request.data.get('city', order.city)
        order.address = request.data.get('address', order.address)
        order.delivery_type = request.data.get('deliveryType', order.delivery_type)
        order.payment_type = request.data.get('paymentType', order.payment_type)
        order.comment = request.data.get('comment', order.comment)
        if order.delivery_type == 'delivery' and order.total_cost < 2000:
            order.total_cost += 200
        elif order.delivery_type == 'express':
            order.total_cost += 500
        order.save()
        return Response({"orderId": order.id})
