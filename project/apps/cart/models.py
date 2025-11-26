
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.products.models import Product, ProductVariant


class Cart(models.Model):
    """نموذج سلة التسوق"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name=_('المستخدم'),
        related_name='cart',
        null=True,
        blank=True
    )
    session_key = models.CharField(
        _('مفتاح الجلسة'), 
        max_length=40, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('سلة التسوق')
        verbose_name_plural = _('سلال التسوق')

    def __str__(self):
        if self.user:
            return f"سلة {self.user.username}"
        return f"سلة الجلسة {self.session_key}"

    def get_total_price(self):
        """حساب الإجمالي لسلة التسوق"""
        total = sum(item.get_total_price() for item in self.items.all())
        return total

    def get_total_items(self):
        """حساب إجمالي العناصر في سلة التسوق"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """نموذج عناصر سلة التسوق"""
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        verbose_name=_('سلة التسوق'),
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name=_('المنتج')
    )
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        verbose_name=_('متغير المنتج'),
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(_('الكمية'), default=1)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('عنصر سلة التسوق')
        verbose_name_plural = _('عناصر سلة التسوق')
        unique_together = ('cart', 'product', 'variant')

    def __str__(self):
        if self.variant:
            return f"{self.product.name} - {self.variant.sku}"
        return self.product.name

    def get_price(self):
        """الحصول على سعر العنصر"""
        if self.variant:
            return self.variant.price
        return self.product.price

    def get_total_price(self):
        """الحصول على الإجمالي للعنصر"""
        return self.get_price() * self.quantity

    def get_compare_price(self):
        """الحصول على سعر المقارنة"""
        if self.variant:
            return self.variant.compare_price
        return self.product.compare_price

    def get_discount_percentage(self):
        """الحصول على نسبة الخصم"""
        price = self.get_price()
        compare_price = self.get_compare_price()
        if compare_price and compare_price > price:
            return int((compare_price - price) / compare_price * 100)
        return None

    def get_image(self):
        """الحصول على صورة المنتج"""
        if self.variant and self.variant.image:
            return self.variant.image.image.url
        elif self.product.images.filter(is_featured=True).exists():
            return self.product.images.filter(is_featured=True).first().image.url
        elif self.product.images.exists():
            return self.product.images.first().image.url
        return None
