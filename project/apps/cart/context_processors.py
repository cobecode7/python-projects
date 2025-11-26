
from .models import Cart, CartItem


def cart(request):
    """معالج سياق سلة التسوق"""
    cart = None
    cart_items_count = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            pass
    else:
        session_key = request.session.get('cart_session_key')
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key)
                cart_items_count = sum(item.quantity for item in cart.items.all())
            except Cart.DoesNotExist:
                pass

    return {
        'cart': cart,
        'cart_items_count': cart_items_count,
    }
