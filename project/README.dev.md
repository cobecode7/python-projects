
# دليل التطوير للمتجر الإلكتروني

هذا الدليل يشرح كيفية إعداد بيئة التطوير للمشروع باستخدام Docker و uv.

## المتطلبات الأساسية

- Docker و Docker Compose
- Git

## إعداد المشروع

1. استنساخ المستودع:
```bash
git clone <repository-url>
cd ecommerce
```

2. إنشاء ملف .env:
```bash
cp .env.example .env
# قم بتعديل المتغيرات في ملف .env حسب الحاجة
```

3. بناء وتشغيل الحاويات:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

## الأوامر الشائعة

### تشغيل المشروع
```bash
docker-compose -f docker-compose.dev.yml up
```

### إيقاف المشروع
```bash
docker-compose -f docker-compose.dev.yml down
```

### عرض سجلات الحاويات
```bash
docker-compose -f docker-compose.dev.yml logs -f
```

### تنفيذ الأوامر داخل حاوية الويب
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py <command>
```

### إنشاء ترحيلات قاعدة البيانات
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py makemigrations
```

### تطبيق الترحيلات
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
```

### إنشاء مستخدم مدير
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

### جمع الملفات الثابتة
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py collectstatic
```

### تشغيل الاختبارات
```bash
docker-compose -f docker-compose.dev.yml exec web pytest
```

### فحص جودة الكود
```bash
docker-compose -f docker-compose.dev.yml exec web ruff check .
```

### تنسيق الكود
```bash
docker-compose -f docker-compose.dev.yml exec web ruff format .
```

## الوصول إلى الخدمات

- الموقع: http://localhost:8000
- لوحة تحكم Django: http://localhost:8000/admin
- قاعدة البيانات: localhost:5432
- Redis: localhost:6379

## هيكل المشروع

```
ecommerce/
├── apps/               # تطبيقات Django
│   ├── users/          # تطبيق المستخدمين
│   ├── products/       # تطبيق المنتجات
│   ├── orders/         # تطبيق الطلبات
│   ├── payments/       # تطبيق الدفعات
│   ├── reviews/        # تطبيق التقييمات
│   ├── coupons/        # تطبيق الكوبونات
│   ├── notifications/  # تطبيق الإشعارات
│   └── wishlist/       # تطبيق قائمة الرغبات
├── config/             # إعدادات المشروع
│   ├── settings/       # ملفات الإعدادات
│   ├── urls.py         # مسارات المشروع
│   ├── wsgi.py         # WSGI
│   └── asgi.py         # ASGI
├── static/             # الملفات الثابتة
├── media/              # الملفات المرفوعة
├── templates/          # قوالب HTML
├── tests/              # الاختبارات
├── requirements.txt    # الاعتماديات
├── Dockerfile          # ملف Docker
├── docker-compose.yml  # ملف Docker Compose
└── manage.py           # ملف إدارة Django
```

## الممارسات الموصى بها

1. استخدم git للتحكم في الإصدارات
2. اكتب اختبارات للكود الجديد
3. استخدم ruff لفحص وتنسيق الكود
4. اتبع أفضل ممارسات Django
5. قم بمراجعة الكود قبل إرساله

## المشاكل الشائعة وحلولها

### مشكلة في الاتصال بقاعدة البيانات
تأكد من أن حاوية قاعدة البيانات تعمل:
```bash
docker-compose -f docker-compose.dev.yml ps db
```

### مشكلة في الملفات الثابتة
تأكد من جمع الملفات الثابتة:
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput
```

### مشكلة في الصلاحيات
إذا واجهت مشاكل في الصلاحيات، يمكنك استخدام:
```bash
sudo chown -R $USER:$USER .
```
