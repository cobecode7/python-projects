
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Payment, Transaction


@receiver(post_save, sender=Payment)
def create_transaction(sender, instance, created, **kwargs):
    """
    إنشاء معاملة عند تغيير حالة الدفع
    """
    if not created:  # تحديث وليس إنشاء
        try:
            old_payment = Payment.objects.get(pk=instance.pk)
            if old_payment.status != instance.status:
                # إنشاء معاملة جديدة
                transaction_type = None

                if instance.status == 'completed' and old_payment.status != 'completed':
                    transaction_type = 'payment'
                elif instance.status == 'refunded' and old_payment.status != 'refunded':
                    transaction_type = 'refund'
                elif instance.status == 'partially_refunded' and old_payment.status != 'partially_refunded':
                    transaction_type = 'refund'

                if transaction_type:
                    Transaction.objects.create(
                        payment=instance,
                        transaction_type=transaction_type,
                        amount=instance.amount if transaction_type == 'payment' else instance.refund_amount,
                        status='completed' if instance.status in ['completed', 'refunded', 'partially_refunded'] else 'pending',
                        transaction_id=instance.transaction_id if transaction_type == 'payment' else instance.refund_transaction_id,
                        completed_at=timezone.now() if instance.status in ['completed', 'refunded', 'partially_refunded'] else None
                    )
        except Payment.DoesNotExist:
            pass
