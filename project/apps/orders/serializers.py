
from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory
from apps.products.serializers import ProductListSerializer as ProductSerializer, ProductVariantSerializer
from apps.users.serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """مسلسل عناصر الطلب"""
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'variant', 'product_name', 'product_sku', 
            'product_image', 'price', 'compare_price', 'quantity', 'total'
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """مسلسل سجل حالة الطلب"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'status', 'status_display', 'notes', 
            'created_at', 'created_by', 'created_by_name'
        ]


class OrderSerializer(serializers.ModelSerializer):
    """مسلسل الطلبات"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'status_display',
            'shipping_address', 'billing_address', 'shipping_method', 
            'shipping_cost', 'tracking_number', 'payment_method', 
            'payment_status', 'transaction_id', 'subtotal', 'tax', 
            'discount', 'total', 'notes', 'created_at', 'updated_at',
            'shipped_at', 'delivered_at', 'items', 'status_history'
        ]
        read_only_fields = [
            'order_number', 'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        ]
