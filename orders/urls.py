from django.urls import path
from .views import BasketView, OrdersView, OrderDetailView

urlpatterns = [
    path('basket', BasketView.as_view(), name='basket'),
    path('orders', OrdersView.as_view(), name='orders'),
    path('order/<int:id>', OrderDetailView.as_view(), name='order-detail'),
]
