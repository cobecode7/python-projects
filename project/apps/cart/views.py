
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.db import transaction
from django.contrib.sessions.models import Session
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from apps.products.models import Product, ProductVariant
from .serializers import CartSerializer, CartItemSerializer


def get_or_create_cart(request):
    """الحصول على سلة التسوق الحالية أو إنشاء سلة جديدة"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # إذا كان المستخدم لديه سلة قديمة مرتبطة بالجلسة، نقل العناصر
        if not created and request.session.get('cart_session_key'):
            try:
                session_cart = Cart.objects.get(session_key=request.session.get('cart_session_key'))
                for item in session_cart.items.all():
                    cart_item, item_created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=item.product,
                        variant=item.variant,
                        defaults={'quantity': item.quantity}
                    )
                    if not item_created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                session_cart.delete()
                request.session.pop('cart_session_key', None)
            except Cart.DoesNotExist:
                pass
    else:
        session_key = request.session.get('cart_session_key')
        if not session_key:
            # إنشاء جلسة جديدة إذا لم تكن موجودة
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            request.session['cart_session_key'] = session_key

        cart, created = Cart.objects.get_or_create(session_key=session_key)

    return cart


class CartDetailView(APIView):
    """عرض تفاصيل سلة التسوق"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddToCartView(APIView):
    """إضافة منتج إلى سلة التسوق"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        product_id = request.data.get('product_id')
        variant_id = request.data.get('variant_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response(
                {'error': _('يجب تحديد المنتج')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id, status='published')
        except Product.DoesNotExist:
            return Response(
                {'error': _('المنتج غير موجود')},
                status=status.HTTP_404_NOT_FOUND
            )

        variant = None
        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id, product=product, is_active=True)
            except ProductVariant.DoesNotExist:
                return Response(
                    {'error': _('متغير المنتج غير موجود')},
                    status=status.HTTP_404_NOT_FOUND
                )

        # التحقق من الكمية
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': _('الكمية غير صالحة')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # التحقق من توفر المنتج
        product_to_check = variant if variant else product
        if product_to_check.track_quantity and product_to_check.quantity < quantity:
            return Response(
                {'error': _('الكمية المطلوبة غير متوفرة')},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = get_or_create_cart(request)

        with transaction.atomic():
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=variant,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)


class UpdateCartItemView(APIView):
    """تحديث كمية عنصر في سلة التسوق"""
    permission_classes = [permissions.AllowAny]

    def put(self, request, item_id):
        try:
            cart = get_or_create_cart(request)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {'error': _('العنصر غير موجود في سلة التسوق')},
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get('quantity')
        if quantity is None:
            return Response(
                {'error': _('يجب تحديد الكمية')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': _('الكمية غير صالحة')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # التحقق من توفر المنتج
        product_to_check = cart_item.variant if cart_item.variant else cart_item.product
        if product_to_check.track_quantity and product_to_check.quantity < quantity:
            return Response(
                {'error': _('الكمية المطلوبة غير متوفرة')},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)


class RemoveFromCartView(APIView):
    """إزالة عنصر من سلة التسوق"""
    permission_classes = [permissions.AllowAny]

    def delete(self, request, item_id):
        try:
            cart = get_or_create_cart(request)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {'error': _('العنصر غير موجود في سلة التسوق')},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()

        serializer = CartSerializer(cart)
        return Response(serializer.data)


class ClearCartView(APIView):
    """تفريغ سلة التسوق"""
    permission_classes = [permissions.AllowAny]

    def delete(self, request):
        cart = get_or_create_cart(request)
        cart.items.all().delete()

        serializer = CartSerializer(cart)
        return Response(serializer.data)


# واجهات HTML
def cart_detail(request):
    """عرض صفحة سلة التسوق"""
    cart = get_or_create_cart(request)
    context = {
        'cart': cart,
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
@login_required
def merge_carts(request):
    """دمج سلة التسوق للضيف مع سلة المستخدم بعد تسجيل الدخول"""
    if request.user.is_authenticated:
        session_key = request.session.get('cart_session_key')
        if session_key:
            try:
                session_cart = Cart.objects.get(session_key=session_key)
                user_cart, created = Cart.objects.get_or_create(user=request.user)

                with transaction.atomic():
                    for item in session_cart.items.all():
                        cart_item, item_created = CartItem.objects.get_or_create(
                            cart=user_cart,
                            product=item.product,
                            variant=item.variant,
                            defaults={'quantity': item.quantity}
                        )
                        if not item_created:
                            cart_item.quantity += item.quantity
                            cart_item.save()

                    session_cart.delete()
                    request.session.pop('cart_session_key', None)

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'})
            except Cart.DoesNotExist:
                pass

    return redirect('cart:cart_detail')
