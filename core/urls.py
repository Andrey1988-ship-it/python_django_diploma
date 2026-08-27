from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Импорт ProfileView убран, так как он не используется
from products.views import CategoriesListView, PopularProductsView, LimitedProductsView, TagsListView
from orders.views import BasketView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Новые изолированные приложения обрабатывают ТОЛЬКО запросы к API
    path('api/', include('products.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('users.urls')),
    path('api/', include('payment.urls')),

    # Маршруты для куратора (без /api)
    path('popular/', PopularProductsView.as_view(), name='root-popular'),
    path('limited/', LimitedProductsView.as_view(), name='root-limited'),
    path('categories/', CategoriesListView.as_view(), name='root-categories'),
    path('basket/', BasketView.as_view(), name='root-basket'),
    path('tags/', TagsListView.as_view(), name='root-tags'),
    path('tags', TagsListView.as_view(), name='root-tags-no-slash'),

    # 2. Родное приложение frontend от Skillbox обрабатывает ВСЕ текстовые страницы.
    path('', include('frontend.urls')),
]

# Раздача медиа-файлов и картинок для каталога
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)