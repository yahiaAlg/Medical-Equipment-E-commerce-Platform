from django.utils import timezone
from decimal import Decimal
from .models import (
    Order,
    OrderItem,
    PaymentProof,
    Notification,
    Refund,
)


class OrderService:
    """Service for order creation and management"""

    @staticmethod
    def create_order_from_cart(user, cart, shipping_data):
        """Create order from cart items"""
        # Get shipping type
        shipping_type = shipping_data.get("shipping_type")
        shipping_cost = shipping_type.cost if shipping_type else Decimal("500.00")

        # Calculate totals
        subtotal = cart.get_total_price()
        tax_rate = Decimal("0.19")  # 19% tax
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount + shipping_cost

        # Create order
        order = Order.objects.create(
            user=user,
            status="pending_confirmation",  # Changed from awaiting_payment
            shipping_type=shipping_type,
            shipping_address=shipping_data["shipping_address"],
            shipping_city=shipping_data["shipping_city"],
            shipping_state=shipping_data["shipping_state"],
            shipping_zip=shipping_data["shipping_zip"],
            shipping_country="Algeria",
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            total_amount=total,
        )

        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )

            # Reduce stock
            product = cart_item.product
            product.stock_quantity -= cart_item.quantity
            product.save()

        # Clear cart
        cart.items.all().delete()

        return order


class PaymentService:
    """Service for payment processing"""

    @staticmethod
    def verify_payment(payment_proof, admin_user, approved, rejection_reason=None):
        """Verify or reject payment proof"""
        if approved:
            payment_proof.verified = True
            payment_proof.verified_by = admin_user
            payment_proof.verified_at = timezone.now()
        else:
            payment_proof.rejection_reason = rejection_reason

        payment_proof.save()
        return payment_proof


class RefundService:
    """Service for refund management"""

    @staticmethod
    def initiate_refund(order, amount, reason, admin_user, complaint=None):
        """Initiate refund for an order"""
        refund = Refund.objects.create(
            order=order,
            invoice=order.invoice,
            complaint=complaint,
            amount=amount,
            reason=reason,
            status="refund_approved",
            approved_by=admin_user,
            approved_at=timezone.now(),
        )

        # Update order status
        order.status = "refund_pending"
        order.save()

        return refund


class NotificationService:
    """Service for creating notifications"""

    @staticmethod
    def create_notification(user, notification_type, title, message, **related_objects):
        """Create a notification for user"""
        return Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            **related_objects
        )

    @staticmethod
    def mark_as_read(notification_ids, user):
        """Mark notifications as read"""
        Notification.objects.filter(id__in=notification_ids, user=user).update(
            is_read=True
        )

    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for user"""
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)


class ReportService:
    """Service for generating reports"""

    @staticmethod
    def get_order_statistics(date_from=None, date_to=None):
        """Get order statistics"""
        from django.db.models import Count, Sum, Avg

        queryset = Order.objects.all()
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return {
            "total_orders": queryset.count(),
            "total_revenue": queryset.filter(
                status__in=["paid", "processing", "shipped", "delivered"]
            ).aggregate(total=Sum("total_amount"))["total"]
            or 0,
            "by_status": queryset.values("status").annotate(count=Count("id")),
            "average_order_value": queryset.aggregate(avg=Avg("total_amount"))["avg"]
            or 0,
        }

    @staticmethod
    def get_payment_statistics():
        """Get payment statistics"""
        from django.db.models import Count

        return {
            "pending_verifications": PaymentProof.objects.filter(
                verified=False
            ).count(),
            "verified_payments": PaymentProof.objects.filter(verified=True).count(),
            "rejected_payments": PaymentProof.objects.exclude(
                rejection_reason=""
            ).count(),
        }

    @staticmethod
    def get_complaint_statistics():
        """Get complaint statistics"""
        from .models import Complaint
        from django.db.models import Count

        return {
            "open_complaints": Complaint.objects.filter(status="open").count(),
            "in_review": Complaint.objects.filter(status="in_review").count(),
            "resolved_complaints": Complaint.objects.filter(status="resolved").count(),
            "by_reason": Complaint.objects.values("reason__name").annotate(
                count=Count("id")
            ),
        }

    @staticmethod
    def get_refund_statistics():
        """Get refund statistics"""
        from django.db.models import Sum

        return {
            "pending_refunds": Refund.objects.filter(status="refund_pending").count(),
            "completed_refunds": Refund.objects.filter(
                status="refund_completed"
            ).count(),
            "total_refunded": Refund.objects.filter(
                status="refund_completed"
            ).aggregate(total=Sum("amount"))["total"]
            or 0,
        }
