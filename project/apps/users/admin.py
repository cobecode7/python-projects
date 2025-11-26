
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Address, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """إعدادات إدارة المستخدمين"""
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_verified')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified', 'groups')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('المعلومات الشخصية'), {'fields': ('username', 'first_name', 'last_name', 'phone', 'birth_date', 'avatar')}),
        (_('الصلاحيات'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        (_('التواريخ'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """إعدادات إدارة العناوين"""
    list_display = ('user', 'first_name', 'last_name', 'city', 'country', 'type', 'default')
    list_filter = ('type', 'default', 'country')
    search_fields = ('user__email', 'first_name', 'last_name', 'city', 'state')

    fieldsets = (
        (_('المعلومات الأساسية'), {'fields': ('user', 'type', 'default')}),
        (_('معلومات العنوان'), {'fields': ('first_name', 'last_name', 'company', 'address_line_1', 
                                           'address_line_2', 'city', 'state', 'postal_code', 'country')}),
        (_('معلومات الاتصال'), {'fields': ('phone',)}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """إعدادات إدارة ملفات تعريف المستخدمين"""
    list_display = ('user', 'location', 'email_notifications', 'push_notifications')
    list_filter = ('email_notifications', 'push_notifications', 'sms_notifications')
    search_fields = ('user__email', 'user__username', 'location', 'bio')

    fieldsets = (
        (_('المعلومات الأساسية'), {'fields': ('user',)}),
        (_('معلومات التعريف'), {'fields': ('bio', 'website', 'location')}),
        (_('وسائل التواصل الاجتماعي'), {'fields': ('facebook', 'twitter', 'instagram', 'linkedin')}),
        (_('إعدادات الإشعارات'), {'fields': ('email_notifications', 'push_notifications', 'sms_notifications')}),
    )
