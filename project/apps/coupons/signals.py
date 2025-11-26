
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import CouponUsage


@receiver(post_save, sender=CouponUsage)
def update_user_coupon(sender, instance, created, **kwargs):
    """
    تحديث كوبون المستخدم عند استخدامه
    """
    if created:
        try:
            from .models import UserCoupon
            user_coupon = UserCoupon.objects.get(
                user=instance.user, 
                coupon=instance.coupon
            )
            user_coupon.is_used = True
            user_coupon.used_at = timezone.now()
            user_coupon.save()
        except UserCoupon.DoesNotExist:
            pass
