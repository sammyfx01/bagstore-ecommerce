from cart.cart import Cart
from wishlist.models import Wishlist


def navigation_counts(request):
    cart_count = len(Cart(request))
    wishlist_count = 0
    order_count = 0

    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).values_list('products', flat=True).count()
        order_count = request.user.orders.count()

    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'order_count': order_count,
    }
