
# استخدام صورة Python الرسمية كصورة أساسية
FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# تعيين دليل العمل
WORKDIR /app

# تثبيت الاعتماديات
COPY pyproject.toml ./
RUN pip install --no-cache-dir uv &&     uv pip install -e .

# نسخ ملفات المشروع
COPY . .

# إنشاء مجلدات للملفات الثابتة والإعلامية
RUN mkdir -p /app/staticfiles /app/media

# جمع الملفات الثابتة
RUN python manage.py collectstatic --noinput

# كشف المنفذ
EXPOSE 8000

# الأمر لتشغيل التطبيق
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
