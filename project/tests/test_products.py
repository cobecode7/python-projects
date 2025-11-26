
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from apps.products.models import Category, Brand, Product, ProductImage, ProductReview
from apps.users.models import User


class ProductModelTest(TestCase):
    """اختبارات نموذج المنتج"""

    def setUp(self):
        self.category = Category.objects.create(
            name='أجهزة إلكترونية',
            slug='electronics'
        )

        self.brand = Brand.objects.create(
            name='سامسونج',
            slug='samsung'
        )

        self.product = Product.objects.create(
            name='هاتف ذكي',
            slug='smartphone',
            description='هاتف ذكي جديد',
            short_description='أحدث هاتف ذكي',
            price=1000.00,
            compare_price=1200.00,
            sku='SP001',
            quantity=10,
            category=self.category,
            brand=self.brand,
            status='published'
        )

    def test_product_creation(self):
        """اختبار إنشاء منتج جديد"""
        self.assertEqual(self.product.name, 'هاتف ذكي')
        self.assertEqual(self.product.slug, 'smartphone')
        self.assertEqual(self.product.price, 1000.00)
        self.assertEqual(self.product.compare_price, 1200.00)
        self.assertEqual(self.product.sku, 'SP001')
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.brand, self.brand)
        self.assertEqual(self.product.status, 'published')

    def test_product_str(self):
        """اختبار تمثيل المنتج كنص"""
        self.assertEqual(str(self.product), 'هاتف ذكي')

    def test_product_is_in_stock(self):
        """اختبار توفر المنتج في المخزون"""
        self.assertTrue(self.product.is_in_stock())

        # اختبار عندما تكون الكمية صفر
        self.product.quantity = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock())

        # اختبار عندما يتم تعطيل تتبع الكمية
        self.product.track_quantity = False
        self.product.save()
        self.assertTrue(self.product.is_in_stock())

    def test_product_get_display_price(self):
        """اختبار الحصول على سعر العرض"""
        self.assertEqual(self.product.get_display_price(), 1000.00)

        # اختبار عندما لا يوجد سعر للمقارنة
        self.product.compare_price = None
        self.product.save()
        self.assertIsNone(self.product.get_display_price())

    def test_product_get_discount_percentage(self):
        """اختبار الحصول على نسبة الخصم"""
        self.assertEqual(self.product.get_discount_percentage(), 17)

        # اختبار عندما لا يوجد سعر للمقارنة
        self.product.compare_price = None
        self.product.save()
        self.assertIsNone(self.product.get_discount_percentage())


class ProductAPITest(APITestCase):
    """اختبارات واجهة برمجة تطبيقات المنتجات"""

    def setUp(self):
        self.category = Category.objects.create(
            name='أجهزة إلكترونية',
            slug='electronics'
        )

        self.brand = Brand.objects.create(
            name='سامسونج',
            slug='samsung'
        )

        self.product = Product.objects.create(
            name='هاتف ذكي',
            slug='smartphone',
            description='هاتف ذكي جديد',
            short_description='أحدث هاتف ذكي',
            price=1000.00,
            compare_price=1200.00,
            sku='SP001',
            quantity=10,
            category=self.category,
            brand=self.brand,
            status='published'
        )

        # إضافة صورة للمنتج
        image = SimpleUploadedFile(
            "product.jpg", 
            b"file_content", 
            content_type="image/jpeg"
        )
        ProductImage.objects.create(
            product=self.product,
            image=image,
            is_featured=True
        )

    def test_product_list(self):
        """اختبار قائمة المنتجات"""
        url = reverse('product-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'هاتف ذكي')

    def test_product_detail(self):
        """اختبار تفاصيل المنتج"""
        url = reverse('product-detail', kwargs={'slug': 'smartphone'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'هاتف ذكي')
        self.assertEqual(response.data['slug'], 'smartphone')

    def test_product_search(self):
        """اختبار البحث عن المنتجات"""
        url = reverse('product-search')
        response = self.client.get(url, {'q': 'هاتف'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'هاتف ذكي')

    def test_featured_products(self):
        """اختبار المنتجات المميزة"""
        # جعل المنتج مميزاً
        self.product.featured = True
        self.product.save()

        url = reverse('featured-products')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'هاتف ذكي')

    def test_category_products(self):
        """اختبار منتجات الفئة"""
        url = reverse('category-products', kwargs={'slug': 'electronics'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'هاتف ذكي')

    def test_brand_products(self):
        """اختبار منتجات العلامة التجارية"""
        url = reverse('brand-products', kwargs={'slug': 'samsung'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'هاتف ذكي')


class ProductReviewTest(TestCase):
    """اختبارات تقييمات المنتجات"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )

        self.category = Category.objects.create(
            name='أجهزة إلكترونية',
            slug='electronics'
        )

        self.product = Product.objects.create(
            name='هاتف ذكي',
            slug='smartphone',
            description='هاتف ذكي جديد',
            short_description='أحدث هاتف ذكي',
            price=1000.00,
            sku='SP001',
            quantity=10,
            category=self.category,
            status='published'
        )

    def test_review_creation(self):
        """اختبار إنشاء تقييم جديد"""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title='رائع',
            content='منتج ممتاز جداً',
            is_approved=True
        )

        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.title, 'رائع')
        self.assertEqual(review.content, 'منتج ممتاز جداً')
        self.assertTrue(review.is_approved)

    def test_review_str(self):
        """اختبار تمثيل التقييم كنص"""
        review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title='رائع',
            content='منتج ممتاز جداً',
            is_approved=True
        )

        expected_str = f"{self.product.name} - {self.user.username} - 5"
        self.assertEqual(str(review), expected_str)


class ProductViewTest(TestCase):
    """اختبارات واجهة المنتجات الأمامية"""

    def setUp(self):
        self.client = Client()

        self.category = Category.objects.create(
            name='أجهزة إلكترونية',
            slug='electronics'
        )

        self.product = Product.objects.create(
            name='هاتف ذكي',
            slug='smartphone',
            description='هاتف ذكي جديد',
            short_description='أحدث هاتف ذكي',
            price=1000.00,
            sku='SP001',
            quantity=10,
            category=self.category,
            status='published'
        )

    def test_product_list_view(self):
        """اختبار صفحة قائمة المنتجات"""
        url = reverse('product_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'المنتجات')

    def test_product_detail_view(self):
        """اختبار صفحة تفاصيل المنتج"""
        url = reverse('product_detail', kwargs={'slug': 'smartphone'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'هاتف ذكي')

    def test_category_detail_view(self):
        """اختبار صفحة تفاصيل الفئة"""
        url = reverse('category_detail', kwargs={'slug': 'electronics'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'أجهزة إلكترونية')
