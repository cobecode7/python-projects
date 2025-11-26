
from django.urls import path
from . import views

app_name = 'coupons'

urlpatterns = [
    path('api/apply/', views.apply_coupon, name='apply_coupon'),
    path('api/remove/', views.remove_coupon, name='remove_coupon'),
]
