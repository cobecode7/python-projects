
"""
إعدادات URLs للمشروع
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/coupons/', include('apps.coupons.urls')),
    path('api/cart/', include('apps.cart.urls')),

    # مسارات CKEditor
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# إضافة مسارات الصفحات الرئيسية
urlpatterns += i18n_patterns(
    path('', TemplateView.as_view(template_name='home/index.html'), name='home'),
    path('products/', include('apps.products.urls_frontend')),
    path('cart/', include('apps.cart.urls_frontend')),
    path('orders/', include('apps.orders.urls_frontend')),
    path('account/', include('apps.users.urls_frontend')),
    prefix_default_language=False,
)

# في بيئة التطوير، خدمة الملفات الإعلامية والثابتة
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # إضافة مسارات شريط أدوات التصحيح
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
