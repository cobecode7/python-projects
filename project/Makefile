
.PHONY: help install run test lint format clean migrate superuser shell

help:
	@echo "الأوامر المتاحة:"
	@echo "  install    - تثبيت الاعتماديات"
	@echo "  run        - تشغيل الخادم"
	@echo "  test       - تشغيل الاختبارات"
	@echo "  lint       - فحص جودة الكود"
	@echo "  format     - تنسيق الكود"
	@echo "  clean      - تنظيف الملفات المؤقتة"
	@echo "  migrate    - تطبيق ترحيلات قاعدة البيانات"
	@echo "  superuser  - إنشاء مستخدم مدير"
	@echo "  shell      - فتح شل Django"

install:
	uv venv
	source .venv/bin/activate && uv pip install -e .

run:
	source .venv/bin/activate && python manage.py runserver

test:
	source .venv/bin/activate && pytest

lint:
	source .venv/bin/activate && ruff check .

format:
	source .venv/bin/activate && ruff format .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

migrate:
	source .venv/bin/activate && python manage.py makemigrations
	source .venv/bin/activate && python manage.py migrate

superuser:
	source .venv/bin/activate && python manage.py createsuperuser

shell:
	source .venv/bin/activate && python manage.py shell
