
from rest_framework import serializers
from .models import Payment, PaymentMethod, Transaction
from apps.orders.serializers import OrderSerializer


class PaymentSerializer(serializers.ModelSerializer):
    """مسلسل الدفعات"""
    order = OrderSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'method', 'method_display', 'status', 'status_display',
            'transaction_id', 'gateway_response', 'refund_amount', 'refund_reason',
            'refund_transaction_id', 'created_at', 'updated_at', 'completed_at'
        ]


class PaymentMethodSerializer(serializers.ModelSerializer):
    """مسلسل طرق الدفع"""
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'method', 'method_display', 'is_active', 
            'description', 'icon', 'icon_url', 'config'
        ]

    def get_icon_url(self, obj):
        """الحصول على رابط الأيقونة"""
        if obj.icon:
            return obj.icon.url
        return None


class TransactionSerializer(serializers.ModelSerializer):
    """مسلسل المعاملات"""
    payment = PaymentSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'payment', 'transaction_type', 'type_display', 'amount',
            'status', 'status_display', 'transaction_id', 'gateway_response',
            'created_at', 'updated_at', 'completed_at'
        ]
