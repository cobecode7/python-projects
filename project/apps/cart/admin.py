
from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """عرض عناصر سلة التسوق كعناصر مضمنة في صفحة سلة التسوق"""
    model = CartItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('product', 'variant', 'quantity', 'created_at', 'updated_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """إعدادات عرض سلة التسوق في لوحة التحكم"""
    list_display = ('id', 'user', 'session_key', 'get_total_items', 'get_total_price', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__username', 'session_key')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]

    def get_total_items(self, obj):
        """عرض إجمالي العناصر في سلة التسوق"""
        return obj.get_total_items()
    get_total_items.short_description = 'إجمالي العناصر'

    def get_total_price(self, obj):
        """عرض الإجمالي لسلة التسوق"""
        return obj.get_total_price()
    get_total_price.short_description = 'الإجمالي'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """إعدادات عرض عناصر سلة التسوق في لوحة التحكم"""
    list_display = ('id', 'cart', 'product', 'variant', 'quantity', 'get_total_price', 'created_at')
    list_filter = ('created_at', 'updated_at', 'product__category')
    search_fields = ('product__name', 'cart__user__email', 'cart__user__username', 'cart__session_key')
    readonly_fields = ('created_at', 'updated_at')

    def get_total_price(self, obj):
        """عرض الإجمالي للعنصر"""
        return obj.get_total_price()
    get_total_price.short_description = 'الإجمالي'
