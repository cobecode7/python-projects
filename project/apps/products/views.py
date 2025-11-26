
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import (
    Category, Tag, Brand, Product, ProductImage, 
    ProductVariant, ProductOption, ProductOptionValue,
    ProductVariantOption, ProductReview, ProductReviewImage
)
from .serializers import (
    CategorySerializer, TagSerializer, BrandSerializer, 
    ProductListSerializer, ProductDetailSerializer, ProductVariantSerializer,
    ProductReviewSerializer
)
from .filters import ProductFilter


class StandardResultsSetPagination(PageNumberPagination):
    """ترقيم الصفحات المخصص"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    """عرض مجموعة الفئات"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class BrandViewSet(viewsets.ModelViewSet):
    """عرض مجموعة العلامات التجارية"""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class TagViewSet(viewsets.ModelViewSet):
    """عرض مجموعة الوسوم"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """عرض مجموعة المنتجات"""
    queryset = Product.objects.filter(status='published')
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """تحديد المسلسل حسب الإجراء"""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        """تصفية المنتجات حسب الحالة"""
        queryset = Product.objects.filter(status='published')

        # تصفية حسب التوفر في المخزون
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(
                Q(track_quantity=False) | Q(quantity__gt=0)
            )

        return queryset

    @action(detail=True, methods=['get'])
    def variants(self, request, slug=None):
        """الحصول على متغيرات المنتج"""
        product = self.get_object()
        variants = product.variants.filter(is_active=True)
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """الحصول على تقييمات المنتج"""
        product = self.get_object()
        reviews = product.reviews.filter(is_approved=True)
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_review(self, request, slug=None):
        """إضافة تقييم للمنتج"""
        product = self.get_object()
        user = request.user

        # التحقق من أن المستخدم لم يقم بتقييم المنتج من قبل
        if ProductReview.objects.filter(product=product, user=user).exists():
            return Response(
                {'error': _('لقد قمت بتقييم هذا المنتج من قبل')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # إنشاء تقييم جديد
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductReviewViewSet(viewsets.ModelViewSet):
    """عرض مجموعة تقييمات المنتجات"""
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'user', 'rating', 'is_approved']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']


class ProductSearchView(APIView):
    """عرض البحث عن المنتجات"""

    def get(self, request):
        """البحث عن المنتجات"""
        query = request.query_params.get('q', '')

        if not query:
            return Response(
                {'error': _('يجب إدخال كلمة البحث')},
                status=status.HTTP_400_BAD_REQUEST
            )

        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(short_description__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

        # تطبيق الفلاتر
        products = ProductFilter(request.GET, queryset=products).qs

        # ترقيم الصفحات
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request)

        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class FeaturedProductsView(APIView):
    """عرض المنتجات المميزة"""

    def get(self, request):
        """الحصول على المنتجات المميزة"""
        products = Product.objects.filter(featured=True, status='published')

        # تطبيق الفلاتر
        products = ProductFilter(request.GET, queryset=products).qs

        # ترقيم الصفحات
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request)

        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class CategoryProductsView(APIView):
    """عرض منتجات الفئة"""

    def get(self, request, slug):
        """الحصول على منتجات الفئة"""
        category = get_object_or_404(Category, slug=slug, is_active=True)

        # الحصول على جميع الفئات الفرعية
        categories = [category]
        categories.extend(category.get_descendants())

        products = Product.objects.filter(
            category__in=categories, 
            status='published'
        )

        # تطبيق الفلاتر
        products = ProductFilter(request.GET, queryset=products).qs

        # ترقيم الصفحات
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request)

        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class BrandProductsView(APIView):
    """عرض منتجات العلامة التجارية"""

    def get(self, request, slug):
        """الحصول على منتجات العلامة التجارية"""
        brand = get_object_or_404(Brand, slug=slug, is_active=True)

        products = Product.objects.filter(
            brand=brand, 
            status='published'
        )

        # تطبيق الفلاتر
        products = ProductFilter(request.GET, queryset=products).qs

        # ترقيم الصفحات
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request)

        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class TagProductsView(APIView):
    """عرض منتجات الوسم"""

    def get(self, request, slug):
        """الحصول على منتجات الوسم"""
        tag = get_object_or_404(Tag, slug=slug)

        products = Product.objects.filter(
            tags=tag, 
            status='published'
        )

        # تطبيق الفلاتر
        products = ProductFilter(request.GET, queryset=products).qs

        # ترقيم الصفحات
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request)

        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


# Frontend Views
class ProductListView(ListView):
    """عرض قائمة المنتجات"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        """تصفية المنتجات"""
        queryset = Product.objects.filter(status='published')

        # تطبيق الفلاتر
        queryset = ProductFilter(self.request.GET, queryset=queryset).qs

        return queryset

    def get_context_data(self, **kwargs):
        """إضافة بيانات إضافية للسياق"""
        context = super().get_context_data(**kwargs)

        # إضافة الفئات والوسوم والعلامات التجارية للفلاتر
        context['categories'] = Category.objects.filter(is_active=True)
        context['tags'] = Tag.objects.all()
        context['brands'] = Brand.objects.filter(is_active=True)

        # إضافة معلمات التصفية الحالية
        context['filter'] = ProductFilter(self.request.GET, queryset=self.get_queryset())

        return context


class ProductDetailView(DetailView):
    """عرض تفاصيل المنتج"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        """إضافة بيانات إضافية للسياق"""
        context = super().get_context_data(**kwargs)

        # إضافة المنتجات ذات الصلة
        product = self.get_object()
        context['related_products'] = Product.objects.filter(
            category=product.category,
            status='published'
        ).exclude(id=product.id)[:4]

        # إضافة تقييمات المنتج
        context['reviews'] = product.reviews.filter(is_approved=True)

        # التحقق إذا كان المستخدم قد قام بتقييم المنتج
        if self.request.user.is_authenticated:
            context['user_review'] = product.reviews.filter(user=self.request.user).first()

        return context


class CategoryListView(ListView):
    """عرض قائمة الفئات"""
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        """الحصول على الفئات الرئيسية فقط"""
        return Category.objects.filter(parent=None, is_active=True)


class CategoryDetailView(DetailView):
    """عرض تفاصيل الفئة"""
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        """إضافة بيانات إضافية للسياق"""
        context = super().get_context_data(**kwargs)

        # إضافة المنتجات في الفئة وفئاتها الفرعية
        category = self.get_object()
        categories = [category]
        categories.extend(category.get_descendants())

        products = Product.objects.filter(
            category__in=categories, 
            status='published'
        )

        # تطبيق الفلاتر
        products = ProductFilter(self.request.GET, queryset=products).qs

        # ترقيم الصفحات
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, self.request)

        if page is not None:
            context['products'] = page
            context['is_paginated'] = True
            context['page_obj'] = page
        else:
            context['products'] = products
            context['is_paginated'] = False

        return context


class BrandListView(ListView):
    """عرض قائمة العلامات التجارية"""
    model = Brand
    template_name = 'products/brand_list.html'
    context_object_name = 'brands'

    def get_queryset(self):
        """الحصول على العلامات التجارية النشطة فقط"""
        return Brand.objects.filter(is_active=True)


class BrandDetailView(DetailView):
    """عرض تفاصيل العلامة التجارية"""
    model = Brand
    template_name = 'products/brand_detail.html'
    context_object_name = 'brand'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        """إضافة بيانات إضافية للسياق"""
        context = super().get_context_data(**kwargs)

        # إضافة منتجات العلامة التجارية
        brand = self.get_object()
        products = Product.objects.filter(
            brand=brand, 
            status='published'
        )

        # تطبيق الفلاتر
        products = ProductFilter(self.request.GET, queryset=products).qs

        # ترقيم الصفحات
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, self.request)

        if page is not None:
            context['products'] = page
            context['is_paginated'] = True
            context['page_obj'] = page
        else:
            context['products'] = products
            context['is_paginated'] = False

        return context


class SearchView(ListView):
    """عرض نتائج البحث"""
    model = Product
    template_name = 'products/search.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        """البحث عن المنتجات"""
        query = self.request.GET.get('q', '')

        if not query:
            return Product.objects.none()

        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(short_description__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

        # تطبيق الفلاتر
        products = ProductFilter(self.request.GET, queryset=products).qs

        return products

    def get_context_data(self, **kwargs):
        """إضافة بيانات إضافية للسياق"""
        context = super().get_context_data(**kwargs)

        # إضافة كلمة البحث
        context['query'] = self.request.GET.get('q', '')

        # إضافة الفئات والوسوم والعلامات التجارية للفلاتر
        context['categories'] = Category.objects.filter(is_active=True)
        context['tags'] = Tag.objects.all()
        context['brands'] = Brand.objects.filter(is_active=True)

        # إضافة معلمات التصفية الحالية
        context['filter'] = ProductFilter(self.request.GET, queryset=self.get_queryset())

        return context
