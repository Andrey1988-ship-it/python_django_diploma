from rest_framework import serializers
# Добавили Product и Review в общий импорт моделей текущего приложения
from .models import Category, Tag, Product, Review


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


from rest_framework import serializers
from .models import Category, Tag, Product, Review

class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image']

    def get_image(self, obj):
        if obj.image_src:
            return {"src": obj.image_src.url, "alt": obj.image_alt or obj.title}
        return None


class CategorySerializer(serializers.ModelSerializer):
    # Явно объявляем subcategories с выводом пустых массивов, если подкатегорий нет
    subcategories = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'subcategories']

    def get_image(self, obj):
        if obj.image_src:
            return {"src": obj.image_src.url, "alt": obj.image_alt or obj.title}
        return None

    def get_subcategories(self, obj):
        # Находим дочерние категории
        subs = obj.subcategories.all()
        if subs.exists():
            return SubCategorySerializer(subs, many=True, context=self.context).data
        # ЖЕСТКИЙ ФИКС БАГА [object Object]: возвращаем пустой список, а не null!
        return []



class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    reviews = serializers.IntegerField(source='reviews.count', read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        # УБЕДИТЕСЬ, ЧТО ПОЛЕ 'id' ЗДЕСЬ ЕСТЬ И СТОИТ ПЕРВЫМ:
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



# Дописано в самый конец файла:
class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    date = serializers.DateTimeField(source='date_created', format='%Y-%m-%d %H:%M', read_only=True)

    class Meta:
        model = Review
        fields = ['author', 'text', 'rate', 'date']


# Дописать в самый конец файла products/serializers.py:

class BannerSerializer(serializers.ModelSerializer):
    """Специальный сериализатор для верхнего слайдера под требования фронтенда Мегано"""
    images = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    reviews = serializers.IntegerField(source='reviews.count', read_only=True)
    category = CategorySerializer(read_only=True)

    # Ключевое поле для фронтенда: подставляем правильную ссылку на детальную страницу товара
    href = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'price', 'count', 'name',
            'description', 'free_delivery', 'images', 'tags',
            'reviews', 'sort_index', 'href'
        ]

    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.all()
        if images.exists():
            return [{"src": request.build_absolute_uri(img.image.url) if request else img.image.url,
                     "alt": img.alt or obj.name} for img in images]
        return [{"src": "https://placeholder.com", "alt": obj.name}]

    def get_href(self, obj):
        # Фронтенд SPA ожидает именно такой относительный путь для перехода к товару
        return f"/product/{obj.id}"

class BannerProductSerializer(serializers.ModelSerializer):
    """Специальный сериализатор, который переводит поля товара под макет баннера фронтенда"""
    title = serializers.CharField(source='name')
    image = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'image', 'href', 'description', 'price']

    def get_image(self, obj):
        request = self.context.get('request')
        # Берем первую картинку из галереи товара
        first_img = obj.images.first()
        if first_img and first_img.image:
            url = request.build_absolute_uri(first_img.image.url) if request else first_img.image.url
            return {"src": url, "alt": first_img.alt or obj.name}
        return {"src": "https://placeholder.com", "alt": obj.name}

    def get_href(self, obj):
        return f"/product/{obj.id}"


