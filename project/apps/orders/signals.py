
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStatusHistory


@receiver(pre_save, sender=Order)
def update_order_timestamps(sender, instance, **kwargs):
    """
    تحديث الطوابع الزمنية للطلب بناءً على حالته
    """
    if instance.pk:  # تحديث وليس إنشاء
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            old_status = old_instance.status
            new_status = instance.status

            # تحديث طابع الشحن
            if old_status != 'shipped' and new_status == 'shipped':
                instance.shipped_at = timezone.now()

            # تحديث طابع التسليم
            if old_status != 'delivered' and new_status == 'delivered':
                instance.delivered_at = timezone.now()
        except Order.DoesNotExist:
            pass


@receiver(post_save, sender=Order)
def create_order_status_history(sender, instance, created, **kwargs):
    """
    إنشاء سجل حالة الطلب عند إنشاء الطلب أو تغيير حالته
    """
    if created:
        # إنشاء سجل الحالة الأولي عند إنشاء الطلب
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.status,
            notes=f'تم إنشاء الطلب بالحالة: {instance.get_status_display()}'
        )
    else:
        # التحقق مما إذا كانت الحالة قد تغيرت
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # إنشاء سجل جديد للحالة
                OrderStatusHistory.objects.create(
                    order=instance,
                    status=instance.status,
                    notes=f'تم تغيير الحالة من {old_instance.get_status_display()} إلى {instance.get_status_display()}'
                )
        except Order.DoesNotExist:
            pass
