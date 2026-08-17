from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Новые изолированные приложения обрабатывают ТОЛЬКО запросы к API
    path('api/', include('products.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('users.urls')),
    path('api/', include('payment.urls')),

    # 2. Родное приложение frontend от Skillbox обрабатывает ВСЕ текстовые страницы.
    # Встроенные урлы фронтенда сами знают, как правильно отдавать страницы /sign-in, /catalog и др.
    path('', include('frontend.urls')),
]

# Раздача медиа-файлов и картинок для каталога
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
