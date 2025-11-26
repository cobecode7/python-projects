
from django.contrib import admin
from .models import Payment, PaymentMethod, Transaction


class TransactionInline(admin.TabularInline):
    """عرض المعاملات كعناصر مضمنة في صفحة الدفع"""
    model = Transaction
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fields = (
        'transaction_type', 'amount', 'status', 'transaction_id',
        'created_at', 'updated_at', 'completed_at'
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """إعدادات عرض الدفعات في لوحة التحكم"""
    list_display = (
        'id', 'order', 'amount', 'method', 'status', 
        'transaction_id', 'created_at'
    )
    list_filter = (
        'status', 'method', 'created_at'
    )
    search_fields = (
        'order__order_number', 'transaction_id', 'refund_transaction_id'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'completed_at'
    )
    inlines = [TransactionInline]

    fieldsets = (
        ('معلومات الدفع', {
            'fields': (
                'order', 'amount', 'method', 'status', 'transaction_id'
            )
        }),
        ('معلومات الإرجاع', {
            'fields': (
                'refund_amount', 'refund_reason', 'refund_transaction_id'
            )
        }),
        ('استجابة بوابة الدفع', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('الطوابع الزمنية', {
            'fields': (
                'created_at', 'updated_at', 'completed_at'
            )
        }),
    )


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """إعدادات عرض طرق الدفع في لوحة التحكم"""
    list_display = (
        'name', 'method', 'is_active', 'created_at'
    )
    list_filter = (
        'method', 'is_active', 'created_at'
    )
    search_fields = ('name', 'method')
    readonly_fields = (
        'created_at', 'updated_at'
    )

    fieldsets = (
        ('معلومات الطريقة', {
            'fields': (
                'name', 'method', 'is_active', 'description', 'icon'
            )
        }),
        ('الإعدادات', {
            'fields': ('config',),
            'classes': ('collapse',)
        }),
        ('الطوابع الزمنية', {
            'fields': (
                'created_at', 'updated_at'
            )
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """إعدادات عرض المعاملات في لوحة التحكم"""
    list_display = (
        'id', 'payment', 'transaction_type', 'amount', 'status',
        'transaction_id', 'created_at'
    )
    list_filter = (
        'transaction_type', 'status', 'created_at'
    )
    search_fields = (
        'payment__order__order_number', 'transaction_id'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'completed_at'
    )

    fieldsets = (
        ('معلومات المعاملة', {
            'fields': (
                'payment', 'transaction_type', 'amount', 'status',
                'transaction_id'
            )
        }),
        ('استجابة بوابة الدفع', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('الطوابع الزمنية', {
            'fields': (
                'created_at', 'updated_at', 'completed_at'
            )
        }),
    )
