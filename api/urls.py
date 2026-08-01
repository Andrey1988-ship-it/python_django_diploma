from django.urls import path
from .views import (
    SignInView, SignUpView, SignOutView,
    CategoriesListView, PopularProductsView, LimitedProductsView,
    BasketView, BannersView, CatalogListView, TagsListView,
    ProductDetailView, ProductReviewView,
    OrdersView, OrderDetailView, PaymentView,
    ProfileView, ProfileAvatarView  # Все импорты строго по одному разу
)

urlpatterns = [
    # 1. Авторизация
    path('sign-in', SignInView.as_view(), name='sign-in'),
    path('sign-up', SignUpView.as_view(), name='sign-up'),
    path('sign-out', SignOutView.as_view(), name='sign-out'),

    # 2. Каталог и списки товаров
    path('categories', CategoriesListView.as_view(), name='categories'),
    path('products/popular', PopularProductsView.as_view(), name='popular-products'),
    path('products/limited', LimitedProductsView.as_view(), name='limited-products'),
    path('banners', BannersView.as_view(), name='banners'),

    # Списки тегов (без слэша и со слэшем для безопасности)
    path('tags', TagsListView.as_view(), name='tags'),
    path('tags/', TagsListView.as_view(), name='tags-slash'),

    # Главный каталог (без слэша и со слэшем)
    path('catalog', CatalogListView.as_view(), name='catalog'),
    path('catalog/', CatalogListView.as_view(), name='catalog-slash'),

    # 3. Карточка товара и отзывы
    path('product/<int:id>', ProductDetailView.as_view(), name='product-detail'),
    path('product/<int:id>/review', ProductReviewView.as_view(), name='product-review'),
    path('product/<int:id>/reviews', ProductReviewView.as_view(), name='product-reviews'),
    path('product/<int:id>/reviews/', ProductReviewView.as_view(), name='product-reviews-slash'),

    # 4. Корзина
    path('basket', BasketView.as_view(), name='basket'),

    # 5. Личный кабинет и Аватарки (с поддержкой слэша по запросу фронтенда)
    path('profile', ProfileView.as_view(), name='profile'),
    path('profile/avatar', ProfileAvatarView.as_view(), name='profile-avatar'),
    path('profile/avatar/', ProfileAvatarView.as_view(), name='profile-avatar-slash'),

    # 6. Заказы и Оплата
    path('orders', OrdersView.as_view(), name='orders'),
    path('order/<int:id>', OrderDetailView.as_view(), name='order-detail'),
    path('payment/<int:id>', PaymentView.as_view(), name='payment'),

]
