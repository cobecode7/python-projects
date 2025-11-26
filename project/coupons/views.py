
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from cart.cart import Cart
from .models import Coupon


@require_POST
@csrf_exempt
def apply_coupon(request):
    """
    تطبيق كوبون الخصم على سلة التسوق
    """
    code = request.POST.get('code', '').strip()
    cart = Cart(request)

    if not code:
        return JsonResponse({'error': 'يرجى إدخال كود الكوبون'})

    try:
        coupon = Coupon.objects.get(
            code__iexact=code,
            is_active=True
        )

        # التحقق من صلاحية الكوبون
        if not coupon.is_valid():
            return JsonResponse({'error': 'الكوبون غير صالح أو منتهي الصلاحية'})

        # حساب قيمة الخصم
        cart_total = cart.get_total_price()

        if coupon.discount_type == 'percentage':
            discount = cart_total * (coupon.discount_value / Decimal('100'))
        else:
            discount = min(coupon.discount_value, cart_total)

        # التحقق من الحد الأقصى للخصم
        if coupon.max_discount and discount > coupon.max_discount:
            discount = coupon.max_discount

        # حفظ الكوبون في الجلسة
        request.session['coupon_id'] = coupon.id
        request.session['coupon_code'] = coupon.code
        request.session['coupon_discount'] = float(discount)

        new_total = cart_total + Decimal('10.00') - discount  # 10.00 هو قيمة الشحن

        return JsonResponse({
            'success': True,
            'coupon': {
                'id': coupon.id,
                'code': coupon.code,
                'discount_type': coupon.discount_type,
                'discount_value': float(coupon.discount_value),
                'discount': float(discount)
            },
            'cart_total': float(cart_total),
            'new_total': float(new_total)
        })

    except Coupon.DoesNotExist:
        return JsonResponse({'error': 'كود الكوبون غير صحيح'})


@require_POST
@csrf_exempt
def remove_coupon(request):
    """
    إزالة كوبون الخصم من سلة التسوق
    """
    cart = Cart(request)
    cart_total = cart.get_total_price()

    # إزالة الكوبون من الجلسة
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'coupon_discount' in request.session:
        del request.session['coupon_discount']

    new_total = cart_total + Decimal('10.00')  # 10.00 هو قيمة الشحن

    return JsonResponse({
        'success': True,
        'cart_total': float(cart_total),
        'new_total': float(new_total)
    })
