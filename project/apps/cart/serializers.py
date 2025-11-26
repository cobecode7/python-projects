
from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductListSerializer as ProductSerializer, ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """مسلسل عناصر سلة التسوق"""
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    price = serializers.SerializerMethodField()
    compare_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'variant', 'quantity', 'price', 
            'compare_price', 'discount_percentage', 'total_price', 'image'
        ]

    def get_price(self, obj):
        """الحصول على سعر العنصر"""
        return obj.get_price()

    def get_compare_price(self, obj):
        """الحصول على سعر المقارنة"""
        compare_price = obj.get_compare_price()
        return compare_price if compare_price else None

    def get_discount_percentage(self, obj):
        """الحصول على نسبة الخصم"""
        discount = obj.get_discount_percentage()
        return discount if discount else None

    def get_total_price(self, obj):
        """الحصول على الإجمالي للعنصر"""
        return obj.get_total_price()

    def get_image(self, obj):
        """الحصول على صورة المنتج"""
        image = obj.get_image()
        return image if image else None


class CartSerializer(serializers.ModelSerializer):
    """مسلسل سلة التسوق"""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_items', 'created_at', 'updated_at']

    def get_total_price(self, obj):
        """الحصول على الإجمالي لسلة التسوق"""
        return obj.get_total_price()

    def get_total_items(self, obj):
        """الحصول على إجمالي العناصر في سلة التسوق"""
        return obj.get_total_items()
