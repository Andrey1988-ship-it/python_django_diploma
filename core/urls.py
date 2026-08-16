from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('catalog/[object Object]/', include('frontend.urls')),
    path('admin/', admin.site.urls),

    # ВСЕ ПУТИ API (БЭКЕНД)
    path('api/', include('products.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('users.urls')),
    path('api/', include('payment.urls')),

    # ХИТРЫЙ ТРЮК ДЛЯ SPA-СТРАНИЦ ФРОНТЕНДА
    path('sign-in', include('frontend.urls')),
    path('cart', include('frontend.urls')),
    path('catalog', include('frontend.urls')),
    path('orders', include('frontend.urls')),

    # РОДНОЙ ФРОНТЕНД ДЛЯ ГЛАВНОЙ СТРАНИЦЫ
    path('', include('frontend.urls')),
]

# РАЗРЕШАЕМ РАЗДАЧУ КАРТИНОК ИЗ ПАПКИ MEDIA ПРИ РАЗРАБОТКЕ
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

