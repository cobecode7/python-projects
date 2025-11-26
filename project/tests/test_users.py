
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserModelTest(TestCase):
    """اختبارات نموذج المستخدم"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )

    def test_user_creation(self):
        """اختبار إنشاء مستخدم جديد"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.is_verified)

    def test_user_str(self):
        """اختبار تمثيل المستخدم كنص"""
        self.assertEqual(str(self.user), 'test@example.com')


class UserAPITest(APITestCase):
    """اختبارات واجهة برمجة تطبيقات المستخدمين"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_user_registration(self):
        """اختبار تسجيل مستخدم جديد"""
        self.client.credentials()  # إزالة المصادقة
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(User.objects.get(email='newuser@example.com').is_verified)

    def test_user_login(self):
        """اختبار تسجيل الدخول"""
        self.client.credentials()  # إزالة المصادقة
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """اختبار تسجيل الدخول ببيانات غير صحيحة"""
        self.client.credentials()  # إزالة المصادقة
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout(self):
        """اختبار تسجيل الخروج"""
        url = reverse('logout')
        refresh_token = str(self.token)
        data = {'refresh': refresh_token}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_profile(self):
        """اختبار عرض ملف تعريف المستخدم"""
        url = reverse('user_profile')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_change_password(self):
        """اختبار تغيير كلمة المرور"""
        url = reverse('change_password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    def test_reset_password(self):
        """اختبار إعادة تعيين كلمة المرور"""
        self.client.credentials()  # إزالة المصادقة
        url = reverse('reset_password')
        data = {'email': 'test@example.com'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserViewTest(TestCase):
    """اختبارات واجهة المستخدم الأمامية"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_login_view(self):
        """اختبار صفحة تسجيل الدخول"""
        url = reverse('login_frontend')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'تسجيل الدخول')

    def test_register_view(self):
        """اختبار صفحة التسجيل"""
        url = reverse('register_frontend')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'إنشاء حساب')

    def test_profile_view_requires_login(self):
        """اختبار أن صفحة الملف الشخصي تتطلب تسجيل الدخول"""
        url = reverse('profile_frontend')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)  # إعادة توجيه لصفحة تسجيل الدخول

    def test_profile_view_with_login(self):
        """اختبار صفحة الملف الشخصي بعد تسجيل الدخول"""
        self.client.login(email='test@example.com', password='testpass123')
        url = reverse('profile_frontend')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'الملف الشخصي')
