from django.contrib import admin
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'date_created', 'status', 'total_cost', 'delivery_type', 'is_deleted']
    list_filter = ['status', 'delivery_type', 'is_deleted']
    search_fields = ['id', 'fullName', 'city', 'address']
    inlines = [OrderItemInline] # Состав заказа внутри карточки
