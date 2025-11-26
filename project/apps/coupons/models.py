
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Coupon(models.Model):
    """نموذج الكوبونات"""
    TYPE_CHOICES = [
        ('percentage', _('نسبة مئوية')),
        ('fixed', _('قيمة ثابتة')),
    ]

    # معلومات الكوبون
    code = models.CharField(_('الكود'), max_length=50, unique=True)
    name = models.CharField(_('الاسم'), max_length=100)
    description = models.TextField(_('الوصف'), blank=True)

    # نوع وقيمة الخصم
    discount_type = models.CharField(
        _('نوع الخصم'), 
        max_length=20, 
        choices=TYPE_CHOICES
    )
    discount_value = models.DecimalField(
        _('قيمة الخصم'), 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    # شروط الاستخدام
    minimum_amount = models.DecimalField(
        _('الحد الأدنى للطلب'), 
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    maximum_discount = models.DecimalField(
        _('الحد الأقصى للخصم'), 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )

    # حدود الاستخدام
    usage_limit = models.PositiveIntegerField(
        _('حد الاستخدام'), 
        null=True, 
        blank=True,
        help_text=_('الحد الأقصى لعدد مرات استخدام الكوبون')
    )
    usage_limit_per_user = models.PositiveIntegerField(
        _('حد الاستخدام لكل مستخدم'), 
        null=True, 
        blank=True,
        help_text=_('الحد الأقصى لعدد مرات استخدام الكوبون لكل مستخدم')
    )

    # التاريخ والنشاط
    start_date = models.DateTimeField(_('تاريخ البدء'), default=timezone.now)
    end_date = models.DateTimeField(_('تاريخ الانتهاء'), null=True, blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)

    # المنتجات والفئات المسموح بها
    products = models.ManyToManyField(
        'products.Product', 
        blank=True, 
        verbose_name=_('المنتجات'),
        related_name='coupons'
    )
    categories = models.ManyToManyField(
        'products.Category', 
        blank=True, 
        verbose_name=_('الفئات'),
        related_name='coupons'
    )

    # المستخدمون المسموح لهم
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        blank=True, 
        verbose_name=_('المستخدمون'),
        related_name='coupons'
    )

    # الطوابع الزمنية
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('كوبون')
        verbose_name_plural = _('الكوبونات')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def is_valid(self, user=None, cart_total=None):
        """التحقق من صلاحية الكوبون"""
        # التحقق من النشاط
        if not self.is_active:
            return False, _('الكوبون غير نشط')

        # التحقق من التاريخ
        now = timezone.now()
        if now < self.start_date:
            return False, _('الكوبون غير صالح بعد')

        if self.end_date and now > self.end_date:
            return False, _('انتهت صلاحية الكوبون')

        # التحقق من حد الاستخدام
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, _('تم الوصول إلى الحد الأقصى لاستخدام الكوبون')

        # التحقق من المستخدم
        if self.users.exists() and (not user or user not in self.users.all()):
            return False, _('الكوبون غير متاح لهذا المستخدم')

        # التحقق من حد الاستخدام لكل مستخدم
        if self.usage_limit_per_user and user:
            user_usage_count = CouponUsage.objects.filter(
                coupon=self, 
                user=user
            ).count()
            if user_usage_count >= self.usage_limit_per_user:
                return False, _('تم الوصول إلى الحد الأقصى لاستخدام الكوبون لهذا المستخدم')

        # التحقق من الحد الأدنى للطلب
        if cart_total and self.minimum_amount > 0 and cart_total < self.minimum_amount:
            return False, _('الحد الأدنى للطلب هو {}'.format(self.minimum_amount))

        return True, ''

    def calculate_discount(self, cart_total):
        """حساب قيمة الخصم"""
        if self.discount_type == 'percentage':
            discount = cart_total * (self.discount_value / 100)
            # تطبيق الحد الأقصى للخصم
            if self.maximum_discount and discount > self.maximum_discount:
                discount = self.maximum_discount
        else:
            discount = self.discount_value

        # التأكد من أن الخصم لا يتجاوز إجمالي السلة
        if discount > cart_total:
            discount = cart_total

        return discount

    @property
    def usage_count(self):
        """الحصول على عدد مرات الاستخدام"""
        return CouponUsage.objects.filter(coupon=self).count()


class CouponUsage(models.Model):
    """نموذج استخدامات الكوبونات"""
    coupon = models.ForeignKey(
        Coupon, 
        on_delete=models.CASCADE, 
        verbose_name=_('الكوبون'),
        related_name='usages'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name=_('المستخدم')
    )
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE, 
        verbose_name=_('الطلب'),
        related_name='coupon_usages'
    )
    discount_amount = models.DecimalField(
        _('مبلغ الخصم'), 
        max_digits=10, 
        decimal_places=2
    )
    created_at = models.DateTimeField(_('تاريخ الاستخدام'), auto_now_add=True)

    class Meta:
        verbose_name = _('استخدام الكوبون')
        verbose_name_plural = _('استخدامات الكوبونات')
        unique_together = ('coupon', 'user', 'order')

    def __str__(self):
        return f"{self.user.username} - {self.coupon.code} - {self.discount_amount}"


class UserCoupon(models.Model):
    """نموذج كوبونات المستخدم"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name=_('المستخدم'),
        related_name='user_coupons'
    )
    coupon = models.ForeignKey(
        Coupon, 
        on_delete=models.CASCADE, 
        verbose_name=_('الكوبون'),
        related_name='user_coupons'
    )
    is_used = models.BooleanField(_('تم الاستخدام'), default=False)
    used_at = models.DateTimeField(
        _('تاريخ الاستخدام'), 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)

    class Meta:
        verbose_name = _('كوبون المستخدم')
        verbose_name_plural = _('كوبونات المستخدم')
        unique_together = ('user', 'coupon')

    def __str__(self):
        return f"{self.user.username} - {self.coupon.code}"
