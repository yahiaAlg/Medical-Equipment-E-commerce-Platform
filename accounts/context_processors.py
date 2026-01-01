# Add to accounts/context_processors.py (or create if doesn't exist)


def wishlist_items(request):
    """Add wishlist products to all templates"""
    if request.user.is_authenticated:
        try:
            from products.models import Wishlist

            wishlist = Wishlist.objects.get(user=request.user)
            return {
                "wishlist_products": wishlist.products.all(),
                "wishlist_count": wishlist.products.count(),
            }
        except Wishlist.DoesNotExist:
            return {"wishlist_products": [], "wishlist_count": 0}
    return {"wishlist_products": [], "wishlist_count": 0}
