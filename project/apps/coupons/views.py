
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal

from .models import Coupon, CouponUsage, UserCoupon
from .serializers import CouponSerializer, CouponUsageSerializer, UserCouponSerializer
from .forms import CouponForm, ApplyCouponForm
from apps.cart.views import get_or_create_cart
from apps.cart.models import Cart


class CouponListView(generics.ListAPIView):
    """عرض قائمة الكوبونات المتاحة للمستخدم"""
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Coupon.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).filter(
            models.Q(users__in=[user]) | models.Q(users__isnull=True)
        ).distinct()


class UserCouponListView(generics.ListAPIView):
    """عرض قائمة كوبونات المستخدم"""
    serializer_class = UserCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserCoupon.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_coupon(request):
    """تطبيق كوبون على سلة التسوق"""
    code = request.data.get('code')

    if not code:
        return Response(
            {'error': _('يجب إدخال كود الكوبون')},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
    except Coupon.DoesNotExist:
        return Response(
            {'error': _('كوبون غير صالح')},
            status=status.HTTP_404_NOT_FOUND
        )

    # الحصول على سلة التسوق
    cart = get_or_create_cart(request)
    cart_total = cart.get_total_price()

    # التحقق من صلاحية الكوبون
    is_valid, message = coupon.is_valid(
        user=request.user if request.user.is_authenticated else None,
        cart_total=cart_total
    )

    if not is_valid:
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )

    # حساب الخصم
    discount = coupon.calculate_discount(cart_total)

    # حفظ الكوبون في الجلسة
    request.session['coupon_code'] = coupon.code
    request.session['coupon_discount'] = float(discount)

    return Response({
        'coupon': {
            'code': coupon.code,
            'name': coupon.name,
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value),
            'discount': float(discount)
        },
        'cart_total': float(cart_total),
        'new_total': float(cart_total - discount)
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def remove_coupon(request):
    """إزالة الكوبون من سلة التسوق"""
    # إزالة الكوبون من الجلسة
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)

    # الحصول على سلة التسوق
    cart = get_or_create_cart(request)
    cart_total = cart.get_total_price()

    return Response({
        'cart_total': float(cart_total),
        'new_total': float(cart_total)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def validate_coupon(request):
    """التحقق من صلاحية الكوبون"""
    code = request.GET.get('code')
    cart_total = request.GET.get('cart_total', 0)

    if not code:
        return Response(
            {'error': _('يجب إدخال كود الكوبون')},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        coupon = Coupon.objects.get(code__iexact=code, is_active=True)
    except Coupon.DoesNotExist:
        return Response(
            {'error': _('كوبون غير صالح')},
            status=status.HTTP_404_NOT_FOUND
        )

    # التحقق من صلاحية الكوبون
    is_valid, message = coupon.is_valid(
        user=request.user if request.user.is_authenticated else None,
        cart_total=float(cart_total) if cart_total else None
    )

    if not is_valid:
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )

    # حساب الخصم
    discount = coupon.calculate_discount(float(cart_total) if cart_total else 0)

    return Response({
        'coupon': {
            'code': coupon.code,
            'name': coupon.name,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value),
            'minimum_amount': float(coupon.minimum_amount),
            'maximum_discount': float(coupon.maximum_discount) if coupon.maximum_discount else None,
            'discount': float(discount)
        }
    })


@login_required
def my_coupons(request):
    """صفحة كوبونات المستخدم"""
    # الكوبونات المتاحة
    available_coupons = Coupon.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).filter(
        models.Q(users__in=[request.user]) | models.Q(users__isnull=True)
    ).distinct()

    # كوبونات المستخدم
    user_coupons = UserCoupon.objects.filter(user=request.user)

    context = {
        'available_coupons': available_coupons,
        'user_coupons': user_coupons,
    }

    return render(request, 'coupons/my_coupons.html', context)


@login_required
@require_POST
def claim_coupon(request, coupon_id):
    """استلام كوبون"""
    coupon = get_object_or_404(Coupon, id=coupon_id, is_active=True)

    # التحقق من أن المستخدم لم يستلم الكوبون من قبل
    if UserCoupon.objects.filter(user=request.user, coupon=coupon).exists():
        messages.error(request, _('لقد استلمت هذا الكوبون من قبل'))
        return redirect('coupons:my_coupons')

    # إنشاء كوبون مستخدم جديد
    UserCoupon.objects.create(user=request.user, coupon=coupon)

    messages.success(request, _('تم استلام الكوبون بنجاح'))
    return redirect('coupons:my_coupons')
