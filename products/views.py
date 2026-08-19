from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Category, Product, Tag, Review
from .serializers import CategorySerializer, ProductSerializer, TagSerializer, ReviewSerializer

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
        return Response({
            'items': data,
            'currentPage': self.page.number,
            'lastPage': self.page.paginator.num_pages
        })

class CatalogListView(APIView):
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

        category_id = request.query_params.get('category')
        if category_id and 'object' not in str(category_id):
            # Перестраховка: если товаров в запрашиваемой категории нет, отдаем весь каталог, чтобы не было пустого экрана
            if Product.objects.filter(category_id=category_id, is_deleted=False).exists():
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
