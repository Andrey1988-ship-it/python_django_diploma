from django.contrib import admin
from .models import Product, Category, Tag, Review, ProductImage  # Убедитесь, что импорт есть!


class ProductImageInline(admin.TabularInline):
    """Позволяет добавлять фотографии прямо внутри карточки товара"""
    model = ProductImage
    extra = 3  # Количество пустых полей для загрузки новых фото


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'parent', 'is_deleted')
    list_filter = ('is_deleted', 'parent')
    search_fields = ('title',)

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'count', 'sort_index', 'sales_count', 'limited_edition', 'free_delivery',
                    'is_deleted')
    list_filter = ('limited_edition', 'free_delivery', 'is_deleted', 'category')
    search_fields = ('name', 'description')

    # ПОДКЛЮЧАЕМ ИНЛАЙН СЮДА
    inlines = [ProductImageInline]

    actions = ['restore_products', 'soft_delete_products']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'category', 'tags')
        }),
        ('Экономика и склад', {
            'fields': ('price', 'count')
        }),
        ('Маркетинг и сортировка по ТЗ', {
            'fields': ('sort_index', 'sales_count', 'limited_edition', 'free_delivery')
        }),
    )

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()

    @admin.action(description="Восстановить выбранные товары")
    def restore_products(self, request, queryset):
        queryset.update(is_deleted=False)

    @admin.action(description="Применить мягкое удаление")
    def soft_delete_products(self, request, queryset):
        queryset.update(is_deleted=True)


# ЖЕСТКАЯ РЕГИСТРАЦИЯ МОДЕЛИ КАРТИНОК В АДМИНКЕ
admin.site.register(ProductImage)
# Глобально убираем опасную стандартную кнопку полного удаления записей из базы данных
admin.site.disable_action('delete_selected')
