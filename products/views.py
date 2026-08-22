from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Category, Product, Tag, Review
from .serializers import CategorySerializer, ProductSerializer, TagSerializer, ReviewSerializer
from django.db.models import Q



class CategoriesListView(APIView):
    def get(self, request):
        categories = Category.objects.filter(parent__isnull=True, is_deleted=False)
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

class PopularProductsView(APIView):
    def get(self, request):
        products = Product.objects.filter(is_deleted=False).order_by('sort_index', '-sales_count')[:8]
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

class LimitedProductsView(APIView):
    def get(self, request):
        products = Product.objects.filter(limited_edition=True, is_deleted=False)[:16]
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

class BannersView(APIView):
    def get(self, request):
        print(f"⚡️ БЭК ПОЛУЧИЛ ЗАПРОС: {request.path}")
        products = Product.objects.filter(is_deleted=False).order_by('id')[:3]
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

class TagsListView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        return Response(TagSerializer(tags, many=True).data)

class ProductDetailView(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product, id=id, is_deleted=False)
        data = ProductSerializer(product, context={'request': request}).data
        reviews = product.reviews.all().order_by('-date_created')
        data['reviews'] = ReviewSerializer(reviews, many=True).data
        return Response(data)

class ProductReviewView(APIView):
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


class CatalogPagination(PageNumberPagination):
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        # БЕЗОПАСНЫЙ ФИКС: Проверяем, создалась ли страница во встроенном механизме Django
        current_page = self.page.number if hasattr(self, 'page') and self.page else 1
        last_page = self.page.paginator.num_pages if hasattr(self, 'page') and self.page else 1

        return Response({
            'items': data,
            'currentPage': current_page,
            'lastPage': last_page
        })


class CatalogListView(APIView):
    def get(self, request):
        # 1. Базовый кверисет: берем только активные товары (все 5 штук)
        queryset = Product.objects.filter(is_deleted=False)

        # 2. Фильтр по поисковому имени (срабатывает, только если текст реально ввели)
        name_query = request.query_params.get('filter[name]') or request.query_params.get('query')
        if name_query and str(name_query).strip():
            queryset = queryset.filter(name__icontains=str(name_query).strip())

        # 3. Фильтр по минимальной цене
        min_price = request.query_params.get('filter[minPrice]')
        if min_price and str(min_price).isdigit():
            queryset = queryset.filter(price__gte=float(min_price))

        # 4. Фильтр по максимальной цене
        max_price = request.query_params.get('filter[maxPrice]')
        if max_price and str(max_price).isdigit():
            queryset = queryset.filter(price__lte=float(max_price))

        # 5. Фильтр по бесплатной доставке (активируется, только если пришло строго 'true')
        free_delivery = request.query_params.get('filter[freeDelivery]')
        if free_delivery == 'true':
            queryset = queryset.filter(free_delivery=True)

        # 6. Фильтр по категории (применяется, только если передан реальный ID категории числом)
        category_id = request.query_params.get('category')
        if category_id and str(category_id).isdigit():
            queryset = queryset.filter(category_id=int(category_id))

        # 7. Сортировка полей
        sort_field = request.query_params.get('sort', 'date')
        sort_type = request.query_params.get('sortType', 'dec')
        sort_mapping = {'price': 'price', 'rating': 'sort_index', 'reviews': 'id', 'date': 'id'}
        field = sort_mapping.get(sort_field, 'id')
        if sort_type == 'dec':
            field = f'-{field}'
        queryset = queryset.order_by(field)

        # 8. Пагинация вывода с защитой от пустого сброса страницы
        paginator = CatalogPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        # Если пагинатор вернул пустоту, но товары в базе есть — берем базовый queryset
        final_queryset = paginated_queryset if paginated_queryset is not None and len(paginated_queryset) > 0 else list(
            queryset)

        serializer = ProductSerializer(final_queryset, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

class SalesListView(APIView):
    def get(self, request):
        # Берем товары. Если у вас есть поле "old_price" или "discount" (скидка),
        # замените queryset на: Product.objects.filter(old_price__isnull=False, is_deleted=False)
        # Для простоты возьмем все товары, чтобы не было 404:
        queryset = Product.objects.filter(is_deleted=False)

        # Используем вашу пагинацию (она уже есть в файле)
        paginator = CatalogPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        # Если пагинатор вернул пустоту, берем весь кверисет
        final_queryset = paginated_queryset if paginated_queryset is not None and len(paginated_queryset) > 0 else list(queryset)

        serializer = ProductSerializer(final_queryset, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)



