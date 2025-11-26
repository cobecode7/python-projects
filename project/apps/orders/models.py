
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.products.models import Product, ProductVariant
from apps.users.models import Address


class Order(models.Model):
    """نموذج الطلبات"""
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('confirmed', _('مؤكد')),
        ('processing', _('قيد المعالجة')),
        ('shipped', _('تم الشحن')),
        ('delivered', _('تم التسليم')),
        ('cancelled', _('ملغي')),
        ('refunded', _('مسترد')),
    ]

    # معلومات الطلب
    order_number = models.CharField(_('رقم الطلب'), max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('المستخدم')
    )
    status = models.CharField(
        _('الحالة'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )

    # معلومات الشحن
    shipping_address = models.ForeignKey(
        Address, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='shipping_orders',
        verbose_name=_('عنوان الشحن')
    )
    billing_address = models.ForeignKey(
        Address, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='billing_orders',
        verbose_name=_('عنوان الفوترة')
    )
    shipping_method = models.CharField(
        _('طريقة الشحن'), 
        max_length=100, 
        blank=True
    )
    shipping_cost = models.DecimalField(
        _('تكلفة الشحن'), 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    tracking_number = models.CharField(
        _('رقم التتبع'), 
        max_length=100, 
        blank=True
    )

    # معلومات الدفع
    payment_method = models.CharField(
        _('طريقة الدفع'), 
        max_length=100, 
        blank=True
    )
    payment_status = models.CharField(
        _('حالة الدفع'), 
        max_length=50, 
        blank=True
    )
    transaction_id = models.CharField(
        _('معرف المعاملة'), 
        max_length=100, 
        blank=True
    )

    # التكاليف
    subtotal = models.DecimalField(
        _('المجموع الفرعي'), 
        max_digits=10, 
        decimal_places=2
    )
    tax = models.DecimalField(
        _('الضريبة'), 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    discount = models.DecimalField(
        _('الخصم'), 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    total = models.DecimalField(
        _('الإجمالي'), 
        max_digits=10, 
        decimal_places=2
    )

    # ملاحظات
    notes = models.TextField(_('ملاحظات'), blank=True)

    # الطوابع الزمنية
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    shipped_at = models.DateTimeField(
        _('تاريخ الشحن'), 
        null=True, 
        blank=True
    )
    delivered_at = models.DateTimeField(
        _('تاريخ التسليم'), 
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = _('طلب')
        verbose_name_plural = _('الطلبات')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
            models.Index(fields=['total']),
        ]

    def __str__(self):
        return f"طلب #{self.order_number}"

    def save(self, *args, **kwargs):
        # إنشاء رقم الطلب تلقائياً
        if not self.order_number:
            from django.utils import timezone
            now = timezone.now()
            self.order_number = f"ORD-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """نموذج عناصر الطلب"""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name=_('الطلب')
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_('المنتج')
    )
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('متغير المنتج')
    )

    # معلومات المنتج (للاحتفاظ بها حتى لو تم حذف المنتج)
    product_name = models.CharField(_('اسم المنتج'), max_length=200)
    product_sku = models.CharField(_('رمز المنتج'), max_length=100, blank=True)
    product_image = models.CharField(_('صورة المنتج'), max_length=200, blank=True)

    # التسعير
    price = models.DecimalField(_('السعر'), max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(
        _('سعر للمقارنة'), 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    quantity = models.PositiveIntegerField(_('الكمية'))
    total = models.DecimalField(_('الإجمالي'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('عنصر الطلب')
        verbose_name_plural = _('عناصر الطلب')
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
            models.Index(fields=['variant']),
        ]

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        # حساب الإجمالي تلقائياً
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """نموذج سجل حالة الطلب"""
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='status_history',
        verbose_name=_('الطلب')
    )
    status = models.CharField(
        _('الحالة'), 
        max_length=20, 
        choices=Order.STATUS_CHOICES
    )
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('أنشأ بواسطة')
    )

    class Meta:
        verbose_name = _('سجل حالة الطلب')
        verbose_name_plural = _('سجلات حالة الطلب')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"
