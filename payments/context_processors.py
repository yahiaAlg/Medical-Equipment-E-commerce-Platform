def cart_items_count(request):
    """Add cart items count to all templates"""
    if request.user.is_authenticated:
        try:
            from .models import Cart
            cart = Cart.objects.get(user=request.user)
            return {'cart_items_count': cart.get_total_items()}
        except Cart.DoesNotExist:
            return {'cart_items_count': 0}
    return {'cart_items_count': 0}