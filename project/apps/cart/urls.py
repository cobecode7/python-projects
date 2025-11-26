
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # واجهات API
    path('api/', views.CartDetailView.as_view(), name='cart_detail_api'),
    path('api/add/', views.AddToCartView.as_view(), name='add_to_cart_api'),
    path('api/update/<int:item_id>/', views.UpdateCartItemView.as_view(), name='update_cart_item_api'),
    path('api/remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart_api'),
    path('api/clear/', views.ClearCartView.as_view(), name='clear_cart_api'),

    # واجهات HTML
    path('', views.cart_detail, name='cart_detail'),
    path('merge/', views.merge_carts, name='merge_carts'),
]
