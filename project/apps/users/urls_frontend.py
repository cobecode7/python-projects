
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # صفحات المصادقة
    path('login/', views.LoginViewFrontend.as_view(), name='login_frontend'),
    path('register/', views.RegisterViewFrontend.as_view(), name='register_frontend'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout_frontend'),
    path('password-reset/', views.PasswordResetViewFrontend.as_view(), name='password_reset_frontend'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done_frontend'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm_frontend'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete_frontend'),

    # صفحة الملف الشخصي
    path('profile/', views.ProfileViewFrontend.as_view(), name='profile_frontend'),
    path('profile/edit/', views.EditProfileViewFrontend.as_view(), name='edit_profile_frontend'),

    # صفحات العناوين
    path('addresses/', views.AddressesViewFrontend.as_view(), name='addresses_frontend'),
    path('addresses/add/', views.AddAddressViewFrontend.as_view(), name='add_address_frontend'),
    path('addresses/edit/<int:pk>/', views.EditAddressViewFrontend.as_view(), name='edit_address_frontend'),
    path('addresses/delete/<int:pk>/', views.DeleteAddressViewFrontend.as_view(), name='delete_address_frontend'),

    # صفحة الإعدادات
    path('settings/', views.SettingsViewFrontend.as_view(), name='settings_frontend'),
]
