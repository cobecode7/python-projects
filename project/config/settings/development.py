
"""
إعدادات بيئة التطوير
"""

from .base import *

# تفعيل وضع التصحيح
DEBUG = True

# إضافة المضيفين المحليين
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# إعدادات قاعدة البيانات للتطوير
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# إعدادات البريد الإلكتروني للتطوير
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# إعدادات التخزين المؤقت للتطوير
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# إعدادات الوسائط للتطوير
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# تفعيل أدوات التطوير
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

# تفعيل CORS للتطوير
CORS_ALLOW_ALL_ORIGINS = True

# تفعيل ملفات CSS و JavaScript غير المضغوطة
PIPELINE_ENABLED = False

# إعدادات التخزين المؤقت (لتحسين الأداء في بيئة التطوير)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
