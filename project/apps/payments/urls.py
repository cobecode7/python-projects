
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # واجهات API
    path('api/methods/', views.PaymentMethodListView.as_view(), name='payment_methods_api'),
    path('api/', views.PaymentListView.as_view(), name='payment_list_api'),
    path('api/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail_api'),
    path('api/create/', views.create_payment, name='create_payment_api'),

    # واجهات HTML
    path('order/<int:order_id>/', views.payment_page, name='payment_page'),
    path('paypal/execute/', views.paypal_execute, name='paypal_execute'),

    # إشعارات Webhook
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhook/paypal/', views.paypal_webhook, name='paypal_webhook'),
]
