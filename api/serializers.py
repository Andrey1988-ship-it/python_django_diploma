from rest_framework import serializers
from .models import Category, Product, Tag, Profile, Review

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image']

    def get_image(self, obj):
        if obj.image_src:
            return {"src": obj.image_src.url, "alt": obj.image_alt}
        return None

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'subcategories']

    def get_image(self, obj):
        if obj.image_src:
            return {"src": obj.image_src.url, "alt": obj.image_alt}
        return None


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    reviews = serializers.IntegerField(source='reviews.count', read_only=True)

    # Делаем категорию полноценным вложенным объектом для корректных ссылок фронтенда
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'price', 'count', 'name',
            'description', 'free_delivery', 'images', 'tags',
            'reviews', 'sort_index'
        ]

    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.all()
        if images.exists():
            return [{"src": request.build_absolute_uri(img.image.url) if request else img.image.url,
                     "alt": img.alt or obj.name} for img in images]
        return [{"src": "https://placeholder.com", "alt": obj.name}]


class ProfileSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source='user.first_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['fullName', 'email', 'phone', 'avatar']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            url = request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url

            # ХАК ДЛЯ ФРОНТЕНДА: Передаем параметры ширины прямо в JSON-ответ.
            # Если фронтенд вставляет это в тег <img>, атрибуты сработают автоматически.
            return {
                "src": url,
                "alt": "avatar",
                "width": "150",  # Жестко задаем 150 пикселей
                "height": "150"
            }

        return {"src": "https://placeholder.com", "alt": "default avatar"}

# Добавляем недостающий сериализатор отзывов для детальной страницы товара
class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    date = serializers.DateTimeField(source='date_created', format='%Y-%m-%d %H:%M', read_only=True)

    class Meta:
        model = Review
        fields = ['author', 'text', 'rate', 'date']

