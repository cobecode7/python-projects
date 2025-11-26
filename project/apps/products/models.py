
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.conf import settings


class Category(models.Model):
    """نموذج الفئات"""
    name = models.CharField(_('اسم الفئة'), max_length=100)
    slug = models.SlugField(_('الرابط'), unique=True)
    description = models.TextField(_('الوصف'), blank=True)
    image = models.ImageField(_('صورة الفئة'), upload_to='categories/', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('فئة')
        verbose_name_plural = _('الفئات')
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """نموذج الوسوم"""
    name = models.CharField(_('اسم الوسم'), max_length=50)
    slug = models.SlugField(_('الرابط'), unique=True)

    class Meta:
        verbose_name = _('وسم')
        verbose_name_plural = _('الوسوم')

    def __str__(self):
        return self.name


class Brand(models.Model):
    """نموذج العلامات التجارية"""
    name = models.CharField(_('اسم العلامة التجارية'), max_length=100)
    slug = models.SlugField(_('الرابط'), unique=True)
    description = models.TextField(_('الوصف'), blank=True)
    logo = models.ImageField(_('شعار العلامة التجارية'), upload_to='brands/', blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('علامة تجارية')
        verbose_name_plural = _('العلامات التجارية')
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """نموذج المنتجات"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('published', _('منشور')),
        ('archived', _('مؤرشف')),
    ]

    # معلومات أساسية
    name = models.CharField(_('اسم المنتج'), max_length=200)
    slug = models.SlugField(_('الرابط'), unique=True)
    description = RichTextField(_('الوصف'))
    short_description = models.CharField(_('الوصف المختصر'), max_length=500)

    # التسعير
    price = models.DecimalField(_('السعر'), max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(_('سعر للمقارنة'), max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_item = models.DecimalField(_('التكلفة للوحدة'), max_digits=10, decimal_places=2, null=True, blank=True)

    # المخزون
    sku = models.CharField(_('رمز المنتج'), max_length=100, unique=True)
    barcode = models.CharField(_('الباركود'), max_length=50, blank=True)
    track_quantity = models.BooleanField(_('تتبع الكمية'), default=True)
    quantity = models.IntegerField(_('الكمية'), default=0)

    # الشحن
    weight = models.DecimalField(_('الوزن'), max_digits=10, decimal_places=2, null=True, blank=True)
    requires_shipping = models.BooleanField(_('يتطلب شحن'), default=True)

    # التصنيفات
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('الفئة'))
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('العلامة التجارية'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('الوسوم'))

    # SEO
    meta_title = models.CharField(_('عنوان الصفحة'), max_length=200, blank=True)
    meta_description = models.CharField(_('وصف الصفحة'), max_length=300, blank=True)

    # الحالة
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(_('مميز'), default=False)

    # الطوابع الزمنية
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('منتج')
        verbose_name_plural = _('المنتجات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['status']),
            models.Index(fields=['featured']),
            models.Index(fields=['created_at']),
            models.Index(fields=['price']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def is_in_stock(self):
        """التحقق من توفر المنتج في المخزون"""
        return not self.track_quantity or self.quantity > 0

    def get_display_price(self):
        """الحصول على سعر العرض"""
        if self.compare_price and self.compare_price > self.price:
            return self.price
        return None

    def get_discount_percentage(self):
        """الحصول على نسبة الخصم"""
        if self.compare_price and self.compare_price > self.price:
            return int((self.compare_price - self.price) / self.compare_price * 100)
        return None


class ProductImage(models.Model):
    """نموذج صور المنتجات"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_('المنتج'))
    image = models.ImageField(_('الصورة'), upload_to='products/')
    alt_text = models.CharField(_('النص البديل'), max_length=200, blank=True)
    is_featured = models.BooleanField(_('صورة رئيسية'), default=False)
    sort_order = models.PositiveIntegerField(_('ترتيب'), default=0)

    class Meta:
        verbose_name = _('صورة المنتج')
        verbose_name_plural = _('صور المنتجات')
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.product.name} - {self.id}"


class ProductVariant(models.Model):
    """نموذج متغيرات المنتج"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name=_('المنتج'))
    sku = models.CharField(_('رمز المنتج'), max_length=100, unique=True)
    price = models.DecimalField(_('السعر'), max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(_('سعر للمقارنة'), max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(_('الكمية'), default=0)
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('الصورة'))
    is_active = models.BooleanField(_('نشط'), default=True)

    class Meta:
        verbose_name = _('متغير المنتج')
        verbose_name_plural = _('متغيرات المنتج')

    def __str__(self):
        return f"{self.product.name} - {self.sku}"


class ProductOption(models.Model):
    """نموذج خيارات المنتج"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options', verbose_name=_('المنتج'))
    name = models.CharField(_('اسم الخيار'), max_length=100)  # مثل: اللون، المقاس

    class Meta:
        verbose_name = _('خيار المنتج')
        verbose_name_plural = _('خيارات المنتج')
        unique_together = ('product', 'name')

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductOptionValue(models.Model):
    """نموذج قيم خيارات المنتج"""
    option = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name='values', verbose_name=_('الخيار'))
    value = models.CharField(_('القيمة'), max_length=100)  # مثل: أحمر، XL

    class Meta:
        verbose_name = _('قيمة الخيار')
        verbose_name_plural = _('قيم الخيار')
        unique_together = ('option', 'value')

    def __str__(self):
        return f"{self.option.name}: {self.value}"


class ProductVariantOption(models.Model):
    """نموذج ربط متغيرات المنتج بالخيارات"""
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, verbose_name=_('المتغير'))
    option_value = models.ForeignKey(ProductOptionValue, on_delete=models.CASCADE, verbose_name=_('قيمة الخيار'))

    class Meta:
        verbose_name = _('خيار متغير المنتج')
        verbose_name_plural = _('خيارات متغير المنتج')
        unique_together = ('variant', 'option_value')

    def __str__(self):
        return f"{self.variant.sku} - {self.option_value.value}"


class ProductReview(models.Model):
    """نموذج تقييمات المنتجات"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name=_('المنتج'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('المستخدم'))

    rating = models.IntegerField(_('التقييم'), choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(_('العنوان'), max_length=200)
    content = models.TextField(_('المحتوى'))

    is_verified = models.BooleanField(_('موثق'), default=False)
    is_approved = models.BooleanField(_('موافق عليه'), default=False)

    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('تقييم المنتج')
        verbose_name_plural = _('تقييمات المنتجات')
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.product.name} - {self.user.username} - {self.rating}"


class ProductReviewImage(models.Model):
    """نموذج صور تقييمات المنتجات"""
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='images', verbose_name=_('التقييم'))
    image = models.ImageField(_('الصورة'), upload_to='reviews/')

    class Meta:
        verbose_name = _('صورة التقييم')
        verbose_name_plural = _('صور التقييمات')

    def __str__(self):
        return f"{self.review.id} - {self.id}"
