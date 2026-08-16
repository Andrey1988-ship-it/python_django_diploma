from django.contrib import admin
from django.contrib import admin
from .models import Category, Product, Tag, Review, ProductImage

# Позволяет загружать картинки прямо внутри карточки товара
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'parent', 'is_deleted']
    list_filter = ['is_deleted'] # Фильтр мягкого удаления по ТЗ
    search_fields = ['title']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'count', 'sort_index', 'limited_edition', 'is_deleted']
    list_filter = ['limited_edition', 'free_delivery', 'is_deleted']
    search_fields = ['name', 'description']
    inlines = [ProductImageInline] # Картинки внутри товара

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'author', 'rate', 'date_created']
    list_filter = ['rate']
