
from django.contrib import admin
from .models import Coupon, CouponUsage, UserCoupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """إعدادات عرض الكوبونات في لوحة التحكم"""
    list_display = (
        'code', 'name', 'discount_type', 'discount_value', 
        'is_active', 'usage_count', 'start_date', 'end_date'
    )
    list_filter = (
        'discount_type', 'is_active', 'start_date', 'end_date'
    )
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('usage_count', 'created_at', 'updated_at')
    filter_horizontal = ('products', 'categories', 'users')

    fieldsets = (
        ('معلومات الكوبون', {
            'fields': (
                'code', 'name', 'description', 'is_active'
            )
        }),
        ('الخصم', {
            'fields': (
                'discount_type', 'discount_value', 'minimum_amount', 'maximum_discount'
            )
        }),
        ('حدود الاستخدام', {
            'fields': (
                'usage_limit', 'usage_limit_per_user'
            )
        }),
        ('التاريخ والنشاط', {
            'fields': (
                'start_date', 'end_date'
            )
        }),
        ('المنتجات والفئات والمستخدمون', {
            'fields': (
                'products', 'categories', 'users'
            )
        }),
        ('معلومات إضافية', {
            'fields': (
                'usage_count', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """إعدادات عرض استخدامات الكوبونات في لوحة التحكم"""
    list_display = (
        'coupon', 'user', 'order', 'discount_amount', 'created_at'
    )
    list_filter = (
        'coupon', 'created_at'
    )
    search_fields = (
        'coupon__code', 'user__email', 'user__username', 
        'order__order_number'
    )
    readonly_fields = ('created_at',)


@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    """إعدادات عرض كوبونات المستخدم في لوحة التحكم"""
    list_display = (
        'user', 'coupon', 'is_used', 'used_at', 'created_at'
    )
    list_filter = (
        'is_used', 'created_at'
    )
    search_fields = (
        'user__email', 'user__username', 'coupon__code', 'coupon__name'
    )
    readonly_fields = ('created_at',)
