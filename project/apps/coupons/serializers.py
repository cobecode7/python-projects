
from rest_framework import serializers
from .models import Coupon, CouponUsage, UserCoupon
from apps.products.serializers import ProductListSerializer as ProductSerializer, CategorySerializer
from apps.users.serializers import UserSerializer


class CouponSerializer(serializers.ModelSerializer):
    """مسلسل الكوبونات"""
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    users = UserSerializer(many=True, read_only=True)
    usage_count = serializers.ReadOnlyField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'name', 'description', 'discount_type', 'discount_type_display',
            'discount_value', 'minimum_amount', 'maximum_discount', 'usage_limit',
            'usage_limit_per_user', 'start_date', 'end_date', 'is_active',
            'products', 'categories', 'users', 'usage_count', 'created_at', 'updated_at'
        ]


class CouponUsageSerializer(serializers.ModelSerializer):
    """مسلسل استخدامات الكوبونات"""
    coupon = CouponSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = CouponUsage
        fields = [
            'id', 'coupon', 'user', 'order', 'discount_amount', 'created_at'
        ]


class UserCouponSerializer(serializers.ModelSerializer):
    """مسلسل كوبونات المستخدم"""
    coupon = CouponSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserCoupon
        fields = [
            'id', 'coupon', 'user', 'is_used', 'used_at', 'created_at'
        ]
