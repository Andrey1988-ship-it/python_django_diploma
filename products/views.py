from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .serializers import CategorySerializer, ProductSerializer, TagSerializer, ReviewSerializer, BannerSerializer # <-- Добавить BannerSerializer
from .serializers import BannerProductSerializer
# Импортируем модели и сериализаторы из текущего приложения products
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoriesListView(APIView):
    """Вывод древовидного меню: ТОЛЬКО корневые категории (parent=None) по ТЗ"""

    def get(self, request):
        # Выбираем только главные активные категории
        categories = Category.objects.filter(parent__isnull=True, is_deleted=False)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class PopularProductsView(APIView):
    """Блок популярных товаров (топ-8 по индексу и покупкам)"""

    def get(self, request):
        products = Product.objects.filter(is_deleted=False).order_by('sort_index', '-sales_count')[:8]
        return Response(ProductSerializer(products, many=True, context={'request': request}).data)


class LimitedProductsView(APIView):
    """Слайдер товаров ограниченного тиража (до 16 штук)"""

    def get(self, request):
        products = Product.objects.filter(limited_edition=True, is_deleted=False)[:16]
        return Response(ProductSerializer(products, many=True, context={'request': request}).data)


from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Импортируем модели и сериализаторы из текущего приложения products
from .models import Category, Product, Tag, Review
from .serializers import CategorySerializer, ProductSerializer, TagSerializer, ReviewSerializer


class CategoriesListView(APIView):
    """Вывод древовидного меню: ТОЛЬКО корневые категории (parent=None) по ТЗ"""

    def get(self, request):
        categories = Category.objects.filter(parent__isnull=True, is_deleted=False)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class PopularProductsView(APIView):
    """Блок популярных товаров (топ-8 по индексу и покупкам)"""

    def get(self, request):
        products = Product.objects.filter(is_deleted=False).order_by('sort_index', '-sales_count')[:8]
        return Response(ProductSerializer(products, many=True, context={'request': request}).data)


class LimitedProductsView(APIView):
    """Слайдер товаров ограниченного тиража (до 16 штук)"""

    def get(self, request):
        products = Product.objects.filter(limited_edition=True, is_deleted=False)[:16]
        return Response(ProductSerializer(products, many=True, context={'request': request}).data)


class BannersView(APIView):
    """Промо-баннеры для главной страницы"""
    def get(self, request):
        # Берем 3 активных товара
        products = Product.objects.filter(is_deleted=False).order_by('id')[:3]
        serializer = BannerProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)




class TagsListView(APIView):
    """Получение списка доступных тегов для каталога"""

    def get(self, request):
        tags = Tag.objects.all()
        return Response(TagSerializer(tags, many=True).data)


class ProductDetailView(APIView):
    """Детальная карточка товара с галереей и отзывами"""

    def get(self, request, id):
        product = get_object_or_404(Product, id=id, is_deleted=False)
        data = ProductSerializer(product, context={'request': request}).data
        reviews = product.reviews.all().order_by('-date_created')
        data['reviews'] = ReviewSerializer(reviews, many=True).data
        return Response(data)


class ProductReviewView(APIView):
    """Добавление нового отзыва авторизованным покупателем"""

    def post(self, request, id):
        if not request.user.is_authenticated:
            return Response({"error": "Авторизуйтесь"}, status=status.HTTP_401_UNAUTHORIZED)
        product = get_object_or_404(Product, id=id, is_deleted=False)
        Review.objects.create(
            product=product,
            author=request.user,
            text=request.data.get('text', ''),
            rate=int(request.data.get('rate', 5))
        )
        reviews = product.reviews.all().order_by('-date_created')
        return Response(ReviewSerializer(reviews, many=True).data)


# Дописать в самый конец файла products/views.py:

class CatalogPagination(PageNumberPagination):
    """Форматирование разбиения каталога Мегано на страницы"""
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': self.page.paginator.num_pages
        })


class CatalogListView(APIView):
    """Универсальная фильтрация, регистронезависимый поиск и сортировка каталога по ТЗ"""

    def get(self, request):
        queryset = Product.objects.filter(is_deleted=False)

        name_query = request.query_params.get('filter[name]') or request.query_params.get('query')
        if name_query:
            queryset = queryset.filter(name__icontains=name_query)

        min_price = request.query_params.get('filter[minPrice]')
        max_price = request.query_params.get('filter[maxPrice]')
        if min_price: queryset = queryset.filter(price__gte=min_price)
        if max_price: queryset = queryset.filter(price__lte=max_price)

        free_delivery = request.query_params.get('filter[freeDelivery]')
        if free_delivery == 'true': queryset = queryset.filter(free_delivery=True)

        # Безопасный фильтр с защитой от путаницы типов во фронтенде Skillbox
        category_id = request.query_params.get('category')
        if category_id:
            if 'object' in str(category_id):
                pass
            else:
                queryset = queryset.filter(category_id=category_id)

        sort_field = request.query_params.get('sort', 'date')
        sort_type = request.query_params.get('sortType', 'dec')
        sort_mapping = {'price': 'price', 'rating': 'sort_index', 'reviews': 'id', 'date': 'id'}
        field = sort_mapping.get(sort_field, 'id')
        if sort_type == 'dec': field = f'-{field}'
        queryset = queryset.order_by(field)

        paginator = CatalogPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ProductSerializer(paginated_queryset, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
