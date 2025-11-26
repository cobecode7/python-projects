
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'addresses', views.AddressViewSet)

urlpatterns = [
    # مسارات المصادقة
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', views.RefreshTokenView.as_view(), name='token_refresh'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('confirm-reset-password/', views.ConfirmResetPasswordView.as_view(), name='confirm_reset_password'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),

    # مسارات الملف الشخصي
    path('profile/', views.UserProfileDetailView.as_view(), name='user_profile'),

    # مسارات العناوين
    path('', include(router.urls)),
    path('addresses/default/', views.DefaultAddressView.as_view(), name='default_address'),
]
