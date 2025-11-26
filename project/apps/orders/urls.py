
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # واجهات API
    path('api/', views.OrderListView.as_view(), name='order_list_api'),
    path('api/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail_api'),
    path('api/<int:order_id>/status/', views.OrderStatusHistoryView.as_view(), name='order_status_history_api'),

    # واجهات HTML
    path('checkout/', views.checkout, name='checkout'),
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('', views.order_list, name='order_list'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
]
