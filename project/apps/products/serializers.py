
from rest_framework import serializers
from .models import (
    Category, Tag, Brand, Product, ProductImage, 
    ProductVariant, ProductOption, ProductOptionValue,
    ProductVariantOption, ProductReview, ProductReviewImage
)


class CategorySerializer(serializers.ModelSerializer):
    """مسلسل بيانات الفئات"""
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'children', 'product_count', 'is_active']
        read_only_fields = ['id']

    def get_children(self, obj):
        """الحصول على الفئات الفرعية"""
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data

    def get_product_count(self, obj):
        """الحصول على عدد المنتجات في الفئة"""
        return Product.objects.filter(category=obj, status='published').count()


class TagSerializer(serializers.ModelSerializer):
    """مسلسل بيانات الوسوم"""
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'product_count']
        read_only_fields = ['id']

    def get_product_count(self, obj):
        """الحصول على عدد المنتجات بالوسم"""
        return Product.objects.filter(tags=obj, status='published').count()


class BrandSerializer(serializers.ModelSerializer):
    """مسلسل بيانات العلامات التجارية"""
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'product_count', 'is_active']
        read_only_fields = ['id']

    def get_product_count(self, obj):
        """الحصول على عدد المنتجات للعلامة التجارية"""
        return Product.objects.filter(brand=obj, status='published').count()


class ProductImageSerializer(serializers.ModelSerializer):
    """مسلسل بيانات صور المنتجات"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_featured', 'sort_order']
        read_only_fields = ['id']

    def get_image_url(self, obj):
        """الحصول على رابط الصورة"""
        if obj.image:
            return obj.image.url
        return None


class ProductOptionValueSerializer(serializers.ModelSerializer):
    """مسلسل بيانات قيم خيارات المنتج"""

    class Meta:
        model = ProductOptionValue
        fields = ['id', 'value']
        read_only_fields = ['id']


class ProductOptionSerializer(serializers.ModelSerializer):
    """مسلسل بيانات خيارات المنتج"""
    values = ProductOptionValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductOption
        fields = ['id', 'name', 'values']
        read_only_fields = ['id']


class ProductVariantOptionSerializer(serializers.ModelSerializer):
    """مسلسل بيانات خيارات متغيرات المنتج"""
    option_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariantOption
        fields = ['id', 'option_value', 'option_name']
        read_only_fields = ['id']

    def get_option_name(self, obj):
        """الحصول على اسم الخيار"""
        return obj.option_value.option.name


class ProductVariantSerializer(serializers.ModelSerializer):
    """مسلسل بيانات متغيرات المنتج"""
    options = ProductVariantOptionSerializer(source='variantoption_set', many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'price', 'compare_price', 'quantity', 'image', 'image_url', 
                  'discount_percentage', 'is_active', 'options']
        read_only_fields = ['id']

    def get_image_url(self, obj):
        """الحصول على رابط الصورة"""
        if obj.image:
            return obj.image.image.url
        return None

    def get_discount_percentage(self, obj):
        """الحصول على نسبة الخصم"""
        if obj.compare_price and obj.compare_price > obj.price:
            return int((obj.compare_price - obj.price) / obj.compare_price * 100)
        return None


class ProductReviewImageSerializer(serializers.ModelSerializer):
    """مسلسل بيانات صور تقييمات المنتجات"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductReviewImage
        fields = ['id', 'image', 'image_url']
        read_only_fields = ['id']

    def get_image_url(self, obj):
        """الحصول على رابط الصورة"""
        if obj.image:
            return obj.image.url
        return None


class ProductReviewSerializer(serializers.ModelSerializer):
    """مسلسل بيانات تقييمات المنتجات"""
    user_name = serializers.SerializerMethodField()
    images = ProductReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'user_name', 'rating', 'title', 'content', 'is_verified', 
                  'is_approved', 'created_at', 'updated_at', 'images']
        read_only_fields = ['id', 'user', 'is_verified', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        """الحصول على اسم المستخدم"""
        return f"{obj.user.first_name} {obj.user.last_name}"


class ProductListSerializer(serializers.ModelSerializer):
    """مسلسل بيانات قائمة المنتجات"""
    category_name = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'short_description', 'price', 'compare_price', 
                  'category_name', 'brand_name', 'image_url', 'discount_percentage', 
                  'featured', 'average_rating', 'reviews_count', 'created_at']
        read_only_fields = ['id']

    def get_category_name(self, obj):
        """الحصول على اسم الفئة"""
        return obj.category.name

    def get_brand_name(self, obj):
        """الحصول على اسم العلامة التجارية"""
        return obj.brand.name if obj.brand else None

    def get_image_url(self, obj):
        """الحصول على رابط الصورة الرئيسية"""
        featured_image = obj.images.filter(is_featured=True).first()
        if featured_image:
            return featured_image.image.url
        elif obj.images.exists():
            return obj.images.first().image.url
        return None

    def get_discount_percentage(self, obj):
        """الحصول على نسبة الخصم"""
        if obj.compare_price and obj.compare_price > obj.price:
            return int((obj.compare_price - obj.price) / obj.compare_price * 100)
        return None

    def get_average_rating(self, obj):
        """الحصول على متوسط التقييمات"""
        reviews = ProductReview.objects.filter(product=obj, is_approved=True)
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return None

    def get_reviews_count(self, obj):
        """الحصول على عدد التقييمات"""
        return ProductReview.objects.filter(product=obj, is_approved=True).count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """مسلسل بيانات تفاصيل المنتج"""
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    options = ProductOptionSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    discount_percentage = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'short_description', 'price', 'compare_price', 
                  'cost_per_item', 'sku', 'barcode', 'track_quantity', 'quantity', 
                  'weight', 'requires_shipping', 'category', 'brand', 'tags', 'images', 
                  'variants', 'options', 'meta_title', 'meta_description', 'status', 
                  'featured', 'discount_percentage', 'average_rating', 'reviews_count', 
                  'created_at', 'updated_at']
        read_only_fields = ['id']

    def get_discount_percentage(self, obj):
        """الحصول على نسبة الخصم"""
        if obj.compare_price and obj.compare_price > obj.price:
            return int((obj.compare_price - obj.price) / obj.compare_price * 100)
        return None

    def get_average_rating(self, obj):
        """الحصول على متوسط التقييمات"""
        reviews = ProductReview.objects.filter(product=obj, is_approved=True)
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return None

    def get_reviews_count(self, obj):
        """الحصول على عدد التقييمات"""
        return ProductReview.objects.filter(product=obj, is_approved=True).count()
