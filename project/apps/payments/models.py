
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.orders.models import Order


class Payment(models.Model):
    """نموذج الدفعات"""
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('processing', _('قيد المعالجة')),
        ('completed', _('مكتمل')),
        ('failed', _('فشل')),
        ('refunded', _('مسترد')),
        ('partially_refunded', _('مسترد جزئياً')),
    ]

    METHOD_CHOICES = [
        ('credit_card', _('بطاقة ائتمانية')),
        ('paypal', _('باي بال')),
        ('cash_on_delivery', _('الدفع عند الاستلام')),
        ('bank_transfer', _('تحويل بنكي')),
    ]

    # معلومات الدفع
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name=_('الطلب')
    )
    amount = models.DecimalField(_('المبلغ'), max_digits=10, decimal_places=2)
    method = models.CharField(
        _('طريقة الدفع'), 
        max_length=50, 
        choices=METHOD_CHOICES
    )
    status = models.CharField(
        _('الحالة'), 
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='pending'
    )

    # معلومات المعاملة
    transaction_id = models.CharField(
        _('معرف المعاملة'), 
        max_length=100, 
        blank=True
    )
    gateway_response = models.JSONField(
        _('استجابة بوابة الدفع'), 
        default=dict, 
        blank=True
    )

    # معلومات الإرجاع
    refund_amount = models.DecimalField(
        _('مبلغ الإرجاع'), 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    refund_reason = models.TextField(
        _('سبب الإرجاع'), 
        blank=True
    )
    refund_transaction_id = models.CharField(
        _('معرف معاملة الإرجاع'), 
        max_length=100, 
        blank=True
    )

    # الطوابع الزمنية
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    completed_at = models.DateTimeField(
        _('تاريخ الإنجاز'), 
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = _('دفع')
        verbose_name_plural = _('الدفعات')
        ordering = ['-created_at']

    def __str__(self):
        return f"دفع للطلب #{self.order.order_number} - {self.amount}"

    def save(self, *args, **kwargs):
        # تحديث حالة الدفع في الطلب
        if self.pk:
            old_payment = Payment.objects.get(pk=self.pk)
            if old_payment.status != self.status:
                self.update_order_payment_status()
        else:
            # عند إنشاء دفعة جديدة
            self.update_order_payment_status()

        super().save(*args, **kwargs)

    def update_order_payment_status(self):
        """تحديث حالة الدفع في الطلب"""
        from django.db.models import Sum

        order = self.order
        payments = Payment.objects.filter(order=order)

        # حساب المجموع المدفوع
        total_paid = payments.filter(
            status__in=['completed', 'partially_refunded']
        ).aggregate(total=Sum('amount'))['total'] or 0

        # حساب المجموع المسترد
        total_refunded = payments.filter(
            status__in=['refunded', 'partially_refunded']
        ).aggregate(total=Sum('refund_amount'))['total'] or 0

        # تحديث حالة الدفع في الطلب
        if total_paid >= order.total:
            if total_refunded >= order.total:
                order.payment_status = 'refunded'
            elif total_refunded > 0:
                order.payment_status = 'partially_refunded'
            else:
                order.payment_status = 'paid'
        elif total_paid > 0:
            order.payment_status = 'partially_paid'
        else:
            order.payment_status = 'unpaid'

        order.save()


class PaymentMethod(models.Model):
    """نموذج طرق الدفع المتاحة"""
    name = models.CharField(_('الاسم'), max_length=100)
    method = models.CharField(
        _('الطريقة'), 
        max_length=50, 
        choices=Payment.METHOD_CHOICES, 
        unique=True
    )
    is_active = models.BooleanField(_('نشط'), default=True)
    description = models.TextField(_('الوصف'), blank=True)
    config = models.JSONField(_('الإعدادات'), default=dict, blank=True)

    # صورة الطريقة
    icon = models.ImageField(_('الأيقونة'), upload_to='payment_methods/', blank=True)

    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('طريقة دفع')
        verbose_name_plural = _('طرق الدفع')

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """نموذج المعاملات المالية"""
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('completed', _('مكتملة')),
        ('failed', _('فشلت')),
        ('cancelled', _('ملغاة')),
        ('refunded', _('مستردة')),
    ]

    TYPE_CHOICES = [
        ('payment', _('دفع')),
        ('refund', _('إرجاع')),
        ('capture', _('حجز')),
        ('void', _('إلغاء')),
    ]

    # معلومات المعاملة
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.CASCADE, 
        related_name='transactions',
        verbose_name=_('الدفع')
    )
    transaction_type = models.CharField(
        _('نوع المعاملة'), 
        max_length=50, 
        choices=TYPE_CHOICES
    )
    amount = models.DecimalField(_('المبلغ'), max_digits=10, decimal_places=2)
    status = models.CharField(
        _('الحالة'), 
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='pending'
    )

    # معلومات المعاملة
    transaction_id = models.CharField(
        _('معرف المعاملة'), 
        max_length=100, 
        blank=True
    )
    gateway_response = models.JSONField(
        _('استجابة بوابة الدفع'), 
        default=dict, 
        blank=True
    )

    # الطوابع الزمنية
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    completed_at = models.DateTimeField(
        _('تاريخ الإنجاز'), 
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = _('معاملة')
        verbose_name_plural = _('المعاملات')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.get_status_display()}"
