
from django.urls import path
from . import views

app_name = 'coupons'

urlpatterns = [
    # واجهات API
    path('api/', views.CouponListView.as_view(), name='coupon_list_api'),
    path('api/apply/', views.apply_coupon, name='apply_coupon_api'),
    path('api/remove/', views.remove_coupon, name='remove_coupon_api'),
    path('api/validate/', views.validate_coupon, name='validate_coupon_api'),
    path('api/my-coupons/', views.UserCouponListView.as_view(), name='user_coupon_list_api'),

    # واجهات HTML
    path('my-coupons/', views.my_coupons, name='my_coupons'),
    path('claim/<int:coupon_id>/', views.claim_coupon, name='claim_coupon'),
]
