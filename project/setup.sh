#!/bin/bash

# إعداد بيئة المشروع
echo "جاري إعداد بيئة المشروع..."

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "خطأ: Python3 غير مثبت"
    exit 1
fi

# التحقق من وجود pip
if ! command -v pip3 &> /dev/null; then
    echo "تثبيت pip..."
    python3 -m ensurepip --upgrade
fi

# إنشاء بيئة افتراضية إن لم تكن موجودة
if [ ! -d "venv" ]; then
    echo "جاري إنشاء بيئة افتراضية..."
    python3 -m venv venv
fi

# تنشيط البيئة الافتراضية
source venv/bin/activate

# تثبيت الحزم
echo "جاري تثبيت الحزم..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# تثبيت الحزم من pyproject.toml أيضًا
pip3 install .

echo "اكتمل إعداد المشروع!"
echo ""
echo "لتشغيل المشروع:"
echo "1. أنشئ ملف .env بناءً على .env.example"
echo "2. قم بتشغيل: source venv/bin/activate"
echo "3. قم بتشغيل: python manage.py migrate"
echo "4. قم بتشغيل: python manage.py runserver"