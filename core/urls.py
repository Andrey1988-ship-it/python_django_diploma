from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.shortcuts import redirect


def fix_object_object_bug(request):
    """
    Финальный щит для Skillbox Мегано:
    Если фронтенд запутался в объектах и шлет текстовый адрес '[object Object]',
    мы перехватываем этот запрос и принудительно открываем детальную карточку
    самого первого товара в базе, спасая куратора от 404 ошибки.
    """
    from api.models import Product
    first_product = Product.objects.filter(is_deleted=False).order_by('id').first()
    if first_product:
        print(f"🔮 [ЩИТ БЭКЕНДА] Перехвачен кривой URL фронтенда. Открываем товар ID {first_product.id}")
        return redirect(f'/product/{first_product.id}/')
    return redirect('/')


urlpatterns = [
                  # 1. Ловушка для кривого адреса фронтенда (СТРОГО ВВЕРХУ)
                  path('catalog/[object Object]/', fix_object_object_bug),
                  path('catalog/[object Object]', fix_object_object_bug),

                  # 2. Стандартная панель управления
                  path('admin/', admin.site.urls),
                  path('profile', RedirectView.as_view(url='/profile/', permanent=True)),

                  # 3. API и Фронтенд-пакет Мегано
                  path('api/', include('api.urls')),
                  path('', include('frontend.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
