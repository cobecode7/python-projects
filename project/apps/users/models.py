
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """نموذج المستخدم المخصص"""
    email = models.EmailField(_('البريد الإلكتروني'), unique=True)
    phone = models.CharField(_('رقم الهاتف'), max_length=20, blank=True)
    birth_date = models.DateField(_('تاريخ الميلاد'), null=True, blank=True)
    avatar = models.ImageField(_('الصورة الشخصية'), upload_to='avatars/', blank=True)
    is_verified = models.BooleanField(_('مفعل'), default=False)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.email


class Address(models.Model):
    """نموذج العناوين"""
    TYPE_CHOICES = [
        ('shipping', _('شحن')),
        ('billing', _('فوترة')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('المستخدم'))
    type = models.CharField(_('النوع'), max_length=20, choices=TYPE_CHOICES, default='shipping')

    # معلومات العنوان
    first_name = models.CharField(_('الاسم الأول'), max_length=100)
    last_name = models.CharField(_('الاسم الأخير'), max_length=100)
    company = models.CharField(_('الشركة'), max_length=100, blank=True)
    address_line_1 = models.CharField(_('عنوان السطر الأول'), max_length=200)
    address_line_2 = models.CharField(_('عنوان السطر الثاني'), max_length=200, blank=True)
    city = models.CharField(_('المدينة'), max_length=100)
    state = models.CharField(_('الولاية/المنطقة'), max_length=100)
    postal_code = models.CharField(_('الرمز البريدي'), max_length=20)
    country = models.CharField(_('البلد'), max_length=100)
    phone = models.CharField(_('رقم الهاتف'), max_length=20)

    default = models.BooleanField(_('افتراضي'), default=False)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('عنوان')
        verbose_name_plural = _('العناوين')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['city']),
            models.Index(fields=['country']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.city}"


class UserProfile(models.Model):
    """نموذج ملف تعريف المستخدم"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('المستخدم'))
    bio = models.TextField(_('السيرة الذاتية'), blank=True)
    website = models.URLField(_('الموقع الإلكتروني'), blank=True)
    location = models.CharField(_('الموقع'), max_length=100, blank=True)
    facebook = models.URLField(_('فيسبوك'), blank=True)
    twitter = models.URLField(_('تويتر'), blank=True)
    instagram = models.URLField(_('انستغرام'), blank=True)
    linkedin = models.URLField(_('لينكدإن'), blank=True)

    # إعدادات الإشعارات
    email_notifications = models.BooleanField(_('إشعارات البريد الإلكتروني'), default=True)
    push_notifications = models.BooleanField(_('الإشعارات الفورية'), default=True)
    sms_notifications = models.BooleanField(_('إشعارات الرسائل النصية'), default=False)

    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('ملف تعريف المستخدم')
        verbose_name_plural = _('ملفات تعريف المستخدمين')

    def __str__(self):
        return f"ملف تعريف {self.user.username}"
