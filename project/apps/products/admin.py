
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    Category, Tag, Brand, Product, ProductImage, 
    ProductVariant, ProductOption, ProductOptionValue,
    ProductVariantOption, ProductReview, ProductReviewImage
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """إعدادات إدارة الفئات"""
    list_display = ('name', 'slug', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'parent', 'is_active')}),
        (_('الوصف'), {'fields': ('description', 'image')}),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """إعدادات إدارة الوسوم"""
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """إعدادات إدارة العلامات التجارية"""
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'is_active')}),
        (_('الوصف'), {'fields': ('description', 'logo')}),
    )


class ProductImageInline(admin.TabularInline):
    """عرض صور المنتج في صفحة المنتج"""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_featured', 'sort_order')


class ProductVariantInline(admin.TabularInline):
    """عرض متغيرات المنتج في صفحة المنتج"""
    model = ProductVariant
    extra = 1
    fields = ('sku', 'price', 'compare_price', 'quantity', 'image', 'is_active')


class ProductOptionInline(admin.TabularInline):
    """عرض خيارات المنتج في صفحة المنتج"""
    model = ProductOption
    extra = 1
    fields = ('name',)


class ProductOptionValueInline(admin.TabularInline):
    """عرض قيم خيارات المنتج في صفحة الخيار"""
    model = ProductOptionValue
    extra = 1
    fields = ('value',)


class ProductVariantOptionInline(admin.TabularInline):
    """عرض خيارات متغير المنتج في صفحة المتغير"""
    model = ProductVariantOption
    extra = 1
    fields = ('option_value',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """إعدادات إدارة المنتجات"""
    list_display = ('name', 'category', 'brand', 'price', 'quantity', 'status', 'featured', 'created_at')
    list_filter = ('status', 'featured', 'category', 'brand', 'created_at')
    search_fields = ('name', 'sku', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline, ProductOptionInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'brand', 'status', 'featured')
        }),
        (_('الوصف'), {
            'fields': ('short_description', 'description')
        }),
        (_('التسعير'), {
            'fields': ('price', 'compare_price', 'cost_per_item')
        }),
        (_('المخزون'), {
            'fields': ('sku', 'barcode', 'track_quantity', 'quantity')
        }),
        (_('الشحن'), {
            'fields': ('weight', 'requires_shipping')
        }),
        (_('الوسوم'), {
            'fields': ('tags',)
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description')
        }),
    )

    def get_queryset(self, request):
        """تصفية المنتجات حسب المستخدم"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(status='published')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """إعدادات إدارة صور المنتجات"""
    list_display = ('product', 'alt_text', 'is_featured', 'sort_order')
    list_filter = ('is_featured',)
    search_fields = ('product__name', 'alt_text')
    list_editable = ('is_featured', 'sort_order')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """إعدادات إدارة متغيرات المنتجات"""
    list_display = ('product', 'sku', 'price', 'quantity', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('product__name', 'sku')
    inlines = [ProductVariantOptionInline]


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    """إعدادات إدارة خيارات المنتجات"""
    list_display = ('product', 'name')
    search_fields = ('product__name', 'name')
    inlines = [ProductOptionValueInline]


@admin.register(ProductOptionValue)
class ProductOptionValueAdmin(admin.ModelAdmin):
    """إعدادات إدارة قيم خيارات المنتجات"""
    list_display = ('option', 'value')
    search_fields = ('option__name', 'value')


class ProductReviewImageInline(admin.TabularInline):
    """عرض صور التقييم في صفحة التقييم"""
    model = ProductReviewImage
    extra = 1
    fields = ('image',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """إعدادات إدارة تقييمات المنتجات"""
    list_display = ('product', 'user', 'rating', 'is_verified', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'content')
    inlines = [ProductReviewImageInline]

    actions = ['approve_reviews', 'unapprove_reviews']

    def approve_reviews(self, request, queryset):
        """موافقة على التقييمات المحددة"""
        count = queryset.update(is_approved=True)
        self.message_user(request, f'تمت الموافقة على {count} تقييم بنجاح')
    approve_reviews.short_description = _('موافقة على التقييمات المحددة')

    def unapprove_reviews(self, request, queryset):
        """إلغاء موافقة على التقييمات المحددة"""
        count = queryset.update(is_approved=False)
        self.message_user(request, f'تم إلغاء موافقة على {count} تقييم بنجاح')
    unapprove_reviews.short_description = _('إلغاء موافقة على التقييمات المحددة')


@admin.register(ProductReviewImage)
class ProductReviewImageAdmin(admin.ModelAdmin):
    """إعدادات إدارة صور تقييمات المنتجات"""
    list_display = ('review', 'image')
    search_fields = ('review__product__name', 'review__user__username')
