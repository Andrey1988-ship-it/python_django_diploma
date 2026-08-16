from django.urls import path
from .views import (
    CategoriesListView, PopularProductsView, LimitedProductsView,
    BannersView, TagsListView, ProductDetailView, ProductReviewView, CatalogListView
)

urlpatterns = [
    path('categories', CategoriesListView.as_view(), name='categories'),
    path('products/popular', PopularProductsView.as_view(), name='popular-products'),
    path('products/limited', LimitedProductsView.as_view(), name='limited-products'),
    path('banners', BannersView.as_view(), name='banners'),
    path('tags', TagsListView.as_view(), name='tags'),
    path('catalog', CatalogListView.as_view(), name='catalog'),
    path('product/<int:id>', ProductDetailView.as_view(), name='product-detail'),
    path('product/<int:id>/reviews', ProductReviewView.as_view(), name='product-reviews'),
]
