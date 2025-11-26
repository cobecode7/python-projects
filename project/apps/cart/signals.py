
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Cart, CartItem


@receiver(post_save, sender=CartItem)
def update_cart_on_item_change(sender, instance, **kwargs):
    """
    تحديث سلة التسوق عند تغيير عنصر
    """
    # لا حاجة لفعل شيء هنا، لأننا نستخدم طرق النموذج مباشرة
    pass


@receiver(post_delete, sender=CartItem)
def update_cart_on_item_delete(sender, instance, **kwargs):
    """
    تحديث سلة التسوق عند حذف عنصر
    """
    # لا حاجة لفعل شيء هنا، لأننا نستخدم طرق النموذج مباشرة
    pass
