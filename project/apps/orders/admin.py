
from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    """عرض عناصر الطلب كعناصر مضمنة في صفحة الطلب"""
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_sku', 'price', 'compare_price', 'total')
    fields = (
        'product', 'variant', 'product_name', 'product_sku', 'product_image',
        'price', 'compare_price', 'quantity', 'total'
    )


class OrderStatusHistoryInline(admin.TabularInline):
    """عرض سجل حالة الطلب كعناصر مضمنة في صفحة الطلب"""
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at', 'created_by')
    fields = ('status', 'notes', 'created_at', 'created_by')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """إعدادات عرض الطلبات في لوحة التحكم"""
    list_display = (
        'order_number', 'user', 'status', 'payment_status', 
        'total', 'created_at'
    )
    list_filter = (
        'status', 'payment_status', 'payment_method', 
        'shipping_method', 'created_at'
    )
    search_fields = (
        'order_number', 'user__email', 'user__username', 
        'transaction_id', 'tracking_number'
    )
    readonly_fields = (
        'order_number', 'created_at', 'updated_at'
    )
    inlines = [OrderItemInline, OrderStatusHistoryInline]

    fieldsets = (
        ('معلومات الطلب', {
            'fields': (
                'order_number', 'user', 'status', 'notes'
            )
        }),
        ('معلومات الشحن', {
            'fields': (
                'shipping_address', 'billing_address', 'shipping_method', 
                'shipping_cost', 'tracking_number'
            )
        }),
        ('معلومات الدفع', {
            'fields': (
                'payment_method', 'payment_status', 'transaction_id'
            )
        }),
        ('التكاليف', {
            'fields': (
                'subtotal', 'tax', 'discount', 'total'
            )
        }),
        ('الطوابع الزمنية', {
            'fields': (
                'created_at', 'updated_at', 'shipped_at', 'delivered_at'
            )
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """إعدادات عرض عناصر الطلب في لوحة التحكم"""
    list_display = (
        'id', 'order', 'product_name', 'product_sku', 
        'quantity', 'price', 'total'
    )
    list_filter = ('order__status', 'order__created_at')
    search_fields = (
        'order__order_number', 'product_name', 'product_sku'
    )
    readonly_fields = ('total',)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """إعدادات عرض سجل حالة الطلب في لوحة التحكم"""
    list_display = (
        'order', 'status', 'created_by', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'order__order_number', 'notes', 'created_by__email'
    )
    readonly_fields = ('created_at',)
