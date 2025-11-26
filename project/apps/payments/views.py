
import json
import stripe
import paypalrestsdk
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _
from django.conf import settings
from django.db import transaction
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment, PaymentMethod, Transaction
from .serializers import PaymentSerializer, PaymentMethodSerializer, TransactionSerializer
from apps.orders.models import Order


# إعدادات Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# إعدادات PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})


class PaymentMethodListView(generics.ListAPIView):
    """عرض قائمة طرق الدفع المتاحة"""
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True)


class PaymentListView(generics.ListAPIView):
    """عرض قائمة الدفعات"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


class PaymentDetailView(generics.RetrieveAPIView):
    """عرض تفاصيل الدفع"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


@login_required
def payment_page(request, order_id):
    """صفحة الدفع"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # التحقق من حالة الطلب
    if order.payment_status in ['paid', 'partially_paid']:
        messages.warning(request, _('تم دفع هذا الطلب بالفعل'))
        return redirect('orders:order_detail', order_id=order.id)

    # الحصول على طرق الدفع المتاحة
    payment_methods = PaymentMethod.objects.filter(is_active=True)

    context = {
        'order': order,
        'payment_methods': payment_methods,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }

    return render(request, 'payments/payment.html', context)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment(request):
    """إنشاء دفعة جديدة"""
    order_id = request.data.get('order_id')
    method = request.data.get('method')

    if not order_id or not method:
        return Response(
            {'error': _('يجب تحديد الطلب وطريقة الدفع')},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response(
            {'error': _('الطلب غير موجود')},
            status=status.HTTP_404_NOT_FOUND
        )

    # التحقق من حالة الطلب
    if order.payment_status in ['paid', 'partially_paid']:
        return Response(
            {'error': _('تم دفع هذا الطلب بالفعل')},
            status=status.HTTP_400_BAD_REQUEST
        )

    # التحقق من طريقة الدفع
    try:
        payment_method = PaymentMethod.objects.get(method=method, is_active=True)
    except PaymentMethod.DoesNotExist:
        return Response(
            {'error': _('طريقة الدفع غير متوفرة')},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        # إنشاء دفعة جديدة
        payment = Payment.objects.create(
            order=order,
            amount=order.total,
            method=method
        )

        # معالجة الدفع حسب الطريقة
        if method == 'credit_card':
            # معالجة الدفع عبر Stripe
            try:
                # إنشاء عميل Stripe إذا لم يكن موجوداً
                if not request.user.stripe_customer_id:
                    customer = stripe.Customer.create(
                        email=request.user.email,
                        name=request.user.get_full_name() or request.user.username,
                    )
                    request.user.stripe_customer_id = customer.id
                    request.user.save()

                # إنشاء نية الدفع
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total * 100),  # بالسنت
                    currency='sar',  # يمكن تغييره حسب العملة
                    customer=request.user.stripe_customer_id,
                    metadata={
                        'order_id': order.id,
                        'payment_id': payment.id
                    }
                )

                # تحديث الدفع بمعرف المعاملة
                payment.transaction_id = intent.id
                payment.gateway_response = intent.to_dict()
                payment.save()

                return Response({
                    'client_secret': intent.client_secret,
                    'payment_id': payment.id
                })
            except stripe.error.StripeError as e:
                payment.status = 'failed'
                payment.gateway_response = {'error': str(e)}
                payment.save()

                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif method == 'paypal':
            # معالجة الدفع عبر PayPal
            try:
                # إنشاء دفعة PayPal
                payment_data = {
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri(f"/payments/paypal/execute/?payment_id={payment.id}"),
                        "cancel_url": request.build_absolute_uri(f"/orders/{order.id}/")
                    },
                    "transactions": [{
                        "item_list": {
                            "items": [{
                                "name": f"الطلب #{order.order_number}",
                                "sku": order.order_number,
                                "price": str(order.total),
                                "currency": "USD",  # يمكن تغييره حسب العملة
                                "quantity": 1
                            }]
                        },
                        "amount": {
                            "total": str(order.total),
                            "currency": "USD"  # يمكن تغييره حسب العملة
                        },
                        "description": f"دفع للطلب #{order.order_number}"
                    }]
                }

                paypal_payment = paypalrestsdk.Payment.create(payment_data)

                # تحديث الدفع بمعرف المعاملة
                payment.transaction_id = paypal_payment.id
                payment.gateway_response = paypal_payment.to_dict()
                payment.save()

                # الحصول على رابط الموافقة
                for link in paypal_payment.links:
                    if link.rel == "approval_url":
                        approval_url = link.href
                        break

                return Response({
                    'approval_url': approval_url,
                    'payment_id': payment.id
                })
            except paypalrestsdk.exceptions.ConnectionError as e:
                payment.status = 'failed'
                payment.gateway_response = {'error': str(e)}
                payment.save()

                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif method == 'cash_on_delivery':
            # الدفع عند الاستلام
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()

            # تحديث حالة الطلب
            order.payment_status = 'unpaid'  # سيتم الدفع عند الاستلام
            order.status = 'confirmed'
            order.save()

            return Response({
                'status': 'success',
                'message': _('تم تأكيد طلبك بنجاح')
            })

        else:
            return Response(
                {'error': _('طريقة الدفع غير مدعومة')},
                status=status.HTTP_400_BAD_REQUEST
            )


@login_required
def paypal_execute(request):
    """تنفيذ دفع PayPal"""
    payment_id = request.GET.get('payment_id')
    payer_id = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        messages.error(request, _('بيانات الدفع غير صالحة'))
        return redirect('orders:order_list')

    try:
        payment = Payment.objects.get(id=payment_id, order__user=request.user)

        # تنفيذ الدفع
        paypal_payment = paypalrestsdk.Payment.find(payment.transaction_id)

        if paypal_payment.execute({"payer_id": payer_id}):
            # تحديث حالة الدفع
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.gateway_response = paypal_payment.to_dict()
            payment.save()

            # تحديث حالة الطلب
            order = payment.order
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()

            messages.success(request, _('تم دفع طلبك بنجاح'))
            return redirect('orders:order_detail', order_id=order.id)
        else:
            # فشل الدفع
            payment.status = 'failed'
            payment.gateway_response = paypal_payment.to_dict()
            payment.save()

            messages.error(request, _('فشل عملية الدفع'))
            return redirect('orders:order_detail', order_id=payment.order.id)

    except (Payment.DoesNotExist, paypalrestsdk.exceptions.ResourceNotFound):
        messages.error(request, _('الدفع غير موجود'))
        return redirect('orders:order_list')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """معالجة إشعارات Stripe"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # بيانات غير صالحة
        return HttpResponseBadRequest()
    except stripe.error.SignatureVerificationError:
        # توقيع غير صالح
        return HttpResponseBadRequest()

    # معالجة الحدث
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object

        try:
            payment = Payment.objects.get(transaction_id=payment_intent.id)

            # تحديث حالة الدفع
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.gateway_response = payment_intent.to_dict()
            payment.save()

            # تحديث حالة الطلب
            order = payment.order
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
        except Payment.DoesNotExist:
            pass

    return JsonResponse({'status': 'success'})


@csrf_exempt
@require_POST
def paypal_webhook(request):
    """معالجة إشعارات PayPal"""
    # معالجة إشعارات PayPal
    # يمكن تنفيذها حسب الحاجة

    return JsonResponse({'status': 'success'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refund_payment(request, payment_id):
    """إرجاع الدفع"""
    try:
        payment = Payment.objects.get(id=payment_id, order__user=request.user)
    except Payment.DoesNotExist:
        return Response(
            {'error': _('الدفع غير موجود')},
            status=status.HTTP_404_NOT_FOUND
        )

    # التحقق من حالة الدفع
    if payment.status != 'completed':
        return Response(
            {'error': _('لا يمكن إرجاع هذا الدفع')},
            status=status.HTTP_400_BAD_REQUEST
        )

    amount = request.data.get('amount')
    reason = request.data.get('reason', '')

    if not amount:
        return Response(
            {'error': _('يجب تحديد مبلغ الإرجاع')},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        amount = float(amount)
        if amount <= 0 or amount > payment.amount:
            return Response(
                {'error': _('مبلغ الإرجاع غير صالح')},
                status=status.HTTP_400_BAD_REQUEST
            )
    except (ValueError, TypeError):
        return Response(
            {'error': _('مبلغ الإرجاع غير صالح')},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        # معالجة الإرجاع حسب طريقة الدفع
        if payment.method == 'credit_card':
            # معالجة الإرجاع عبر Stripe
            try:
                # إنشاء إرجاع
                refund = stripe.Refund.create(
                    payment_intent=payment.transaction_id,
                    amount=int(amount * 100),  # بالسنت
                    reason=reason or 'requested_by_customer'
                )

                # تحديث حالة الدفع
                if amount == payment.amount:
                    payment.status = 'refunded'
                else:
                    payment.status = 'partially_refunded'

                payment.refund_amount = amount
                payment.refund_reason = reason
                payment.refund_transaction_id = refund.id
                payment.gateway_response.update({'refund': refund.to_dict()})
                payment.save()

                # تحديث حالة الطلب
                order = payment.order
                order.payment_status = 'partially_refunded' if amount < payment.amount else 'refunded'
                order.save()

                return Response({
                    'status': 'success',
                    'message': _('تم إرجاع المبلغ بنجاح')
                })
            except stripe.error.StripeError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif payment.method == 'paypal':
            # معالجة الإرجاع عبر PayPal
            try:
                # إنشاء إرجاع
                sale = paypalrestsdk.Sale.find(payment.gateway_response['transactions'][0]['related_resources'][0]['sale']['id'])
                refund = sale.refund({
                    "amount": {
                        "total": str(amount),
                        "currency": "USD"  # يمكن تغييره حسب العملة
                    }
                })

                if refund.success():
                    # تحديث حالة الدفع
                    if amount == payment.amount:
                        payment.status = 'refunded'
                    else:
                        payment.status = 'partially_refunded'

                    payment.refund_amount = amount
                    payment.refund_reason = reason
                    payment.refund_transaction_id = refund.id
                    payment.gateway_response.update({'refund': refund.to_dict()})
                    payment.save()

                    # تحديث حالة الطلب
                    order = payment.order
                    order.payment_status = 'partially_refunded' if amount < payment.amount else 'refunded'
                    order.save()

                    return Response({
                        'status': 'success',
                        'message': _('تم إرجاع المبلغ بنجاح')
                    })
                else:
                    return Response(
                        {'error': refund.error},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except paypalrestsdk.exceptions.ConnectionError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {'error': _('طريقة الدفع لا تدعم الإرجاع')},
                status=status.HTTP_400_BAD_REQUEST
            )
