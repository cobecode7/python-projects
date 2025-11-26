
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db import transaction
from django.views.decorators.http import require_POST
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import OrderSerializer, OrderItemSerializer, OrderStatusHistorySerializer
from apps.cart.views import get_or_create_cart
from apps.cart.models import CartItem
from apps.users.models import Address


class OrderPagination(PageNumberPagination):
    """ترقيم الصفحات للطلبات"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderListView(generics.ListAPIView):
    """عرض قائمة الطلبات"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = OrderPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    """عرض تفاصيل الطلب"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderStatusHistoryView(generics.ListAPIView):
    """عرض سجل حالة الطلب"""
    serializer_class = OrderStatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return OrderStatusHistory.objects.filter(order_id=order_id, order__user=self.request.user)


@login_required
def checkout(request):
    """صفحة إتمام الطلب"""
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        messages.warning(request, _('سلة التسوق فارغة'))
        return redirect('cart:cart_detail')

    # الحصول على عناوين المستخدم
    addresses = Address.objects.filter(user=request.user)

    # عنوان الشحن الافتراضي
    shipping_address = addresses.filter(type='shipping', default=True).first()

    # عنوان الفوترة الافتراضي
    billing_address = addresses.filter(type='billing', default=True).first()

    context = {
        'cart': cart,
        'addresses': addresses,
        'shipping_address': shipping_address,
        'billing_address': billing_address,
    }

    return render(request, 'orders/checkout.html', context)


@login_required
@require_POST
def create_order(request):
    """إنشاء طلب جديد"""
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        messages.warning(request, _('سلة التسوق فارغة'))
        return redirect('cart:cart_detail')

    shipping_address_id = request.POST.get('shipping_address')
    billing_address_id = request.POST.get('billing_address')
    payment_method = request.POST.get('payment_method')
    notes = request.POST.get('notes', '')

    if not shipping_address_id:
        messages.error(request, _('يجب اختيار عنوان الشحن'))
        return redirect('orders:checkout')

    try:
        shipping_address = Address.objects.get(id=shipping_address_id, user=request.user)
    except Address.DoesNotExist:
        messages.error(request, _('عنوان الشحن غير موجود'))
        return redirect('orders:checkout')

    # عنوان الفوترة
    billing_address = None
    if billing_address_id:
        try:
            billing_address = Address.objects.get(id=billing_address_id, user=request.user)
        except Address.DoesNotExist:
            messages.error(request, _('عنوان الفوترة غير موجود'))
            return redirect('orders:checkout')
    else:
        # استخدام نفس عنوان الشحن للفوترة
        billing_address = shipping_address

    # حساب تكاليف الشحن (يمكن تعديلها لاحقاً)
    shipping_cost = 10  # قيمة ثابتة للتوضيح

    with transaction.atomic():
        # إنشاء الطلب
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=payment_method,
            shipping_cost=shipping_cost,
            subtotal=cart.get_total_price(),
            total=cart.get_total_price() + shipping_cost,
            notes=notes
        )

        # إنشاء عناصر الطلب
        for cart_item in cart.items.all():
            product = cart_item.product
            variant = cart_item.variant

            # الحصول على صورة المنتج
            product_image = ''
            if variant and variant.image:
                product_image = variant.image.image.url
            elif product.images.filter(is_featured=True).exists():
                product_image = product.images.filter(is_featured=True).first().image.url
            elif product.images.exists():
                product_image = product.images.first().image.url

            # الحصول على SKU
            product_sku = product.sku
            if variant:
                product_sku = variant.sku

            # إنشاء عنصر الطلب
            OrderItem.objects.create(
                order=order,
                product=product,
                variant=variant,
                product_name=product.name,
                product_sku=product_sku,
                product_image=product_image,
                price=cart_item.get_price(),
                compare_price=cart_item.get_compare_price(),
                quantity=cart_item.quantity,
                total=cart_item.get_total_price()
            )

            # تحديث كمية المنتج في المخزون
            product_to_update = variant if variant else product
            if product_to_update.track_quantity:
                product_to_update.quantity -= cart_item.quantity
                product_to_update.save()

        # إنشاء سجل حالة الطلب الأولي
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes=_('تم إنشاء الطلب بنجاح'),
            created_by=request.user
        )

        # تفريغ سلة التسوق
        cart.items.all().delete()

    messages.success(request, _('تم إنشاء طلبك بنجاح'))
    return redirect('orders:order_detail', order_id=order.id)


@login_required
def order_detail(request, order_id):
    """عرض تفاصيل الطلب"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    status_history = OrderStatusHistory.objects.filter(order=order).order_by('-created_at')

    context = {
        'order': order,
        'status_history': status_history,
    }

    return render(request, 'orders/order_detail.html', context)


@login_required
def order_list(request):
    """عرض قائمة الطلبات"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'orders': orders,
    }

    return render(request, 'orders/order_list.html', context)


@login_required
@require_POST
def cancel_order(request, order_id):
    """إلغاء الطلب"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # التحقق من إمكانية إلغاء الطلب
    if order.status not in ['pending', 'confirmed']:
        messages.error(request, _('لا يمكن إلغاء هذا الطلب'))
        return redirect('orders:order_detail', order_id=order.id)

    with transaction.atomic():
        # تحديث حالة الطلب
        order.status = 'cancelled'
        order.save()

        # إعادة المنتجات إلى المخزون
        for item in order.items.all():
            product_to_update = item.variant if item.variant else item.product
            if product_to_update.track_quantity:
                product_to_update.quantity += item.quantity
                product_to_update.save()

        # إنشاء سجل حالة الطلب
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            notes=_('تم إلغاء الطلب من قبل العميل'),
            created_by=request.user
        )

    messages.success(request, _('تم إلغاء الطلب بنجاح'))
    return redirect('orders:order_detail', order_id=order.id)
