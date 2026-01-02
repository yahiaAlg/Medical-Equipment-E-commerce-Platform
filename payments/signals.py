from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

from .models import (
    Order,
    Invoice,
    PaymentProof,
    PaymentReceipt,
    Refund,
    RefundProof,
    RefundReceipt,
    Complaint,
    Notification,
)


# At the top, add helper function
def notify_admins(notification_type, title, message, **related_objects):
    """Notify all active admin users"""
    from django.contrib.auth.models import User

    admin_users = User.objects.filter(is_staff=True, is_active=True)
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            notification_type=notification_type,
            title=title,
            message=message,
            **related_objects,
        )


def send_notification_email(user, title, message, notify_admin=False):
    """Helper function to send notification emails"""
    try:
        from pages.models import SiteInformation

        site_info = SiteInformation.get_instance()

        recipient_list = [user.email]
        if notify_admin and site_info.email:
            recipient_list.append(site_info.email)

        send_mail(
            subject=title,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=True,
        )
    except Exception:
        pass


@receiver(post_save, sender=Order)
def create_invoice_on_order(sender, instance, created, **kwargs):
    """Auto-generate invoice when order is created"""
    if created:
        Invoice.objects.create(
            order=instance,
            subtotal=instance.subtotal,
            tax_amount=instance.tax_amount,
            total_amount=instance.total_amount,
            status="unpaid",
        )

        # Create notification for user
        order_msg = f"Your order {instance.order_id} has been placed. Invoice has been generated."
        Notification.objects.create(
            user=instance.user,
            notification_type="order_created",
            title="Order Placed Successfully",
            message=order_msg,
            order=instance,
        )
        send_notification_email(
            instance.user, "Order Placed Successfully", order_msg, notify_admin=True
        )

        # Create notification for invoice
        invoice_msg = f"Invoice {instance.invoice.invoice_number} is now available. Please make payment and upload proof."
        Notification.objects.create(
            user=instance.user,
            notification_type="invoice_created",
            title="Invoice Generated",
            message=invoice_msg,
            order=instance,
            invoice=instance.invoice,
        )
        send_notification_email(instance.user, "Invoice Generated", invoice_msg)

        notify_admins(
            "order_created",
            "New Order Received",
            f"Order {instance.order_id} placed by {instance.user.username} - {instance.total_amount} DZD",
            order=instance,
        )


@receiver(post_save, sender=PaymentProof)
def update_invoice_on_payment_proof(sender, instance, created, **kwargs):
    """Update invoice status when payment proof is uploaded"""
    if created:
        invoice = instance.invoice
        invoice.status = "payment_submitted"
        invoice.save()

        # Update order status
        order = invoice.order
        order.status = "payment_under_review"
        order.save()

        # Notify user
        msg = (
            f"Your payment proof for invoice {invoice.invoice_number} is under review."
        )
        Notification.objects.create(
            user=order.user,
            notification_type="payment_submitted",
            title="Payment Proof Submitted",
            message=msg,
            order=order,
            invoice=invoice,
        )
        send_notification_email(
            order.user, "Payment Proof Submitted", msg, notify_admin=True
        )

        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                notification_type="payment_submitted",
                title="New Payment Proof Submitted",
                message=f"Payment proof for invoice {invoice.invoice_number} needs review.",
                order=order,
                invoice=invoice,
            )


@receiver(post_save, sender=PaymentProof)
def handle_payment_verification(sender, instance, created, **kwargs):
    """Handle payment verification (approve/reject)"""
    if not created and instance.verified:
        invoice = instance.invoice
        order = invoice.order

        # Update invoice
        invoice.status = "paid"
        invoice.paid_at = instance.verified_at or timezone.now()
        invoice.save()

        # Update order
        order.status = "paid"
        order.paid_at = invoice.paid_at
        order.save()

        # Create payment receipt
        if not hasattr(invoice, "receipt"):
            PaymentReceipt.objects.create(
                invoice=invoice,
                payment_proof=instance,
                amount_paid=invoice.total_amount,
                payment_date=invoice.paid_at,
                payment_method=instance.payment_method,
            )

        # Notify user
        msg = f"Your payment for invoice {invoice.invoice_number} has been confirmed. Receipt is now available."
        Notification.objects.create(
            user=order.user,
            notification_type="payment_confirmed",
            title="Payment Confirmed",
            message=msg,
            order=order,
            invoice=invoice,
        )
        send_notification_email(order.user, "Payment Confirmed", msg)

    elif not created and instance.rejection_reason:
        invoice = instance.invoice
        invoice.status = "payment_rejected"
        invoice.save()

        order = invoice.order
        msg = f"Your payment proof for invoice {invoice.invoice_number} was rejected. Reason: {instance.rejection_reason}"

        Notification.objects.create(
            user=order.user,
            notification_type="payment_rejected",
            title="Payment Rejected",
            message=msg,
            order=order,
            invoice=invoice,
        )
        send_notification_email(order.user, "Payment Rejected", msg)


@receiver(post_save, sender=Complaint)
def notify_on_complaint(sender, instance, created, **kwargs):
    """Create notification when complaint is created or updated"""
    if created:
        msg = f"Your complaint {instance.complaint_number} has been submitted and is being reviewed."
        Notification.objects.create(
            user=instance.user,
            notification_type="complaint_created",
            title="Complaint Submitted",
            message=msg,
            order=instance.order,
            complaint=instance,
        )
        send_notification_email(
            instance.user, "Complaint Submitted", msg, notify_admin=True
        )
    else:
        # Status changed
        if instance.status == "resolved":
            msg = f"Your complaint {instance.complaint_number} has been resolved."
            title = "Complaint Resolved"
            Notification.objects.create(
                user=instance.user,
                notification_type="complaint_resolved",
                title=title,
                message=msg,
                order=instance.order,
                complaint=instance,
            )
            send_notification_email(instance.user, title, msg)
        else:
            msg = f"Your complaint {instance.complaint_number} status: {instance.get_status_display()}"
            title = "Complaint Updated"
            Notification.objects.create(
                user=instance.user,
                notification_type="complaint_updated",
                title=title,
                message=msg,
                order=instance.order,
                complaint=instance,
            )
            send_notification_email(instance.user, title, msg)

        notify_admins(
            "complaint_created",
            "New Complaint Submitted",
            f"Complaint {instance.complaint_number} from {instance.user.username} - {instance.reason.name if instance.reason else 'Custom'}",
            order=instance.order,
            complaint=instance,
        )


@receiver(post_save, sender=Refund)
def notify_on_refund(sender, instance, created, **kwargs):
    """Notify user about refund status changes"""
    if created:
        msg = f"A refund of {instance.amount} DZD has been initiated for order {instance.order.order_id}."
        Notification.objects.create(
            user=instance.order.user,
            notification_type="refund_initiated",
            title="Refund Initiated",
            message=msg,
            order=instance.order,
            refund=instance,
        )
        send_notification_email(instance.order.user, "Refund Initiated", msg)
        # Notify other admins
        notify_admins(
            "refund_initiated",
            "Refund Approved",
            f"Refund {instance.refund_number} approved for order {instance.order.order_id} - {instance.amount} DZD",
            order=instance.order,
            refund=instance,
        )


@receiver(post_save, sender=RefundProof)
def complete_refund_on_proof(sender, instance, created, **kwargs):
    """Complete refund when proof is uploaded"""
    if created:
        refund = instance.refund
        refund.status = "refund_completed"
        refund.completed_at = timezone.now()
        refund.save()

        # Update order
        order = refund.order
        order.status = "refunded"
        order.save()

        # Update invoice
        invoice = refund.invoice
        invoice.status = "refunded"
        invoice.save()

        # Create refund receipt
        if not hasattr(refund, "receipt"):
            RefundReceipt.objects.create(
                refund=refund,
                refund_proof=instance,
                amount_refunded=refund.amount,
                refund_date=refund.completed_at,
                refund_method=refund.refund_method,
            )

        # Notify user
        msg = f"Your refund of {refund.amount} DZD has been completed. Receipt is available."
        Notification.objects.create(
            user=order.user,
            notification_type="refund_completed",
            title="Refund Completed",
            message=msg,
            order=order,
            refund=refund,
        )
        send_notification_email(order.user, "Refund Completed", msg)
