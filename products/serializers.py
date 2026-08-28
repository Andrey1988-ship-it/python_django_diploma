from rest_framework import serializers
from .models import Category, Tag, Product, Review


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
        request = self.context.get('request')
        if obj.image_src:
            url = request.build_absolute_uri(obj.image_src.url) if request else obj.image_src.url
            return {"src": url, "alt": obj.image_alt or obj.title}
        return {"src": "", "alt": obj.title}


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'subcategories']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image_src:
            url = request.build_absolute_uri(obj.image_src.url) if request else obj.image_src.url
            return {"src": url, "alt": obj.image_alt or obj.title}
        return {"src": "", "alt": obj.title}

    def get_subcategories(self, obj):
        subs = obj.subcategories.all()
        if subs.exists():
            return CategorySerializer(subs, many=True, context=self.context).data
        return []


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    reviews = serializers.IntegerField(source='reviews.count', read_only=True)

    # Возвращаем объект категории целиком, как в твоем успешном монолите
    category = serializers.IntegerField(source='category.id', read_only=True)


    title = serializers.CharField(source='name', read_only=True)
    price = serializers.FloatField()
    rating = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    freeDelivery = serializers.BooleanField(source='free_delivery', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'price', 'count', 'date', 'title', 'name',
            'description', 'free_delivery', 'freeDelivery', 'images', 'tags',
            'reviews', 'sort_index', 'href', 'rating'
        ]

    def get_rating(self, obj):
        return 5.0

    def get_date(self, obj):
        return "Wed Aug 19 2026 12:00:00 GMT+0300"

    def get_href(self, obj):
        return f"/product/{obj.id}/"

    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.all()
        if images.exists():
            return [{"src": request.build_absolute_uri(img.image.url) if request else img.image.url,
                     "alt": img.alt or obj.name} for img in images]
        return [{"src": "", "alt": obj.name}]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    date = serializers.DateTimeField(source='date_created', format='%Y-%m-%d %H:%M', read_only=True)

    class Meta:
        model = Review
        fields = ['author', 'text', 'rate', 'date']
