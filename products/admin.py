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
    # Показываем все нужные колонки
    list_display = ['id', 'name', 'price', 'count', 'is_deleted']

    # Фильтр справа, чтобы включать/отключать просмотр удаленных
    list_filter = ['is_deleted']

    # Добавляем свои пункты в выпадающий список "Действие"
    actions = ['soft_delete_selected', 'undelete_selected']

    # Мягкое удаление внутри карточки товара
    def delete_model(self, request, obj):
        obj.is_deleted = True
        obj.save()

    # Мягкое удаление массово (через выпадающий список)
    def delete_queryset(self, request, queryset):
        queryset.update(is_deleted=True)

    # Кастомное действие: Мягко удалить
    def soft_delete_selected(self, request, queryset):
        count = queryset.update(is_deleted=True)
        self.message_user(request, f'✅ Мягко удалено {count} товаров.')

    soft_delete_selected.short_description = "Мягко удалить выбранные товары"

    # Кастомное действие: Восстановить
    def undelete_selected(self, request, queryset):
        count = queryset.update(is_deleted=False)
        self.message_user(request, f'✅ Восстановлено {count} товаров.')

    undelete_selected.short_description = "Восстановить выбранные товары"

    def get_queryset(self, request):
        # Используем специальный менеджер all_objects вместо стандартного objects
        return self.model.all_objects.all()

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'author', 'rate', 'date_created']
    list_filter = ['rate']
