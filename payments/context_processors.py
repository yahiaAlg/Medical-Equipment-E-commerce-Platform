from .models import Notification


def notifications(request):
    """Add user notifications to all templates"""
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(user=request.user).order_by(
            "-created_at"
        )[:10]
        unread_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()

        return {
            "notifications": user_notifications,
            "unread_notifications_count": unread_count,
        }
    return {"notifications": [], "unread_notifications_count": 0}


def cart_items_count(request):
    """Add cart items count to all templates"""
    if request.user.is_authenticated:
        try:
            from .models import Cart

            cart = Cart.objects.get(user=request.user)
            return {"cart_items_count": cart.get_total_items()}
        except Cart.DoesNotExist:
            return {"cart_items_count": 0}
    return {"cart_items_count": 0}
