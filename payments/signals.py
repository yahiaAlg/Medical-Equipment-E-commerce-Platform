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


def notify_admins(notification_type, title, message, **related_objects):
    """Notify all active admin users via database notification AND email"""
    admin_users = User.objects.filter(is_staff=True, is_active=True)
    for admin in admin_users:
        # Create database notification
        Notification.objects.create(
            user=admin,
            notification_type=notification_type,
            title=title,
            message=message,
            **related_objects,
        )
        # Send email notification
        send_notification_email(admin, title, message)


def send_notification_email(user, title, message):
    """Helper function to send notification emails"""
    try:
        send_mail(
            subject=title,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception:
        pass


@receiver(post_save, sender=Order)
def handle_order_creation_and_status(sender, instance, created, **kwargs):
    """Handle order creation and status changes"""
    if created:
        # Notify user about order creation
        order_msg = f"Your order {instance.order_id} has been placed and is awaiting confirmation."
        Notification.objects.create(
            user=instance.user,
            notification_type="order_created",
            title="Order Placed Successfully",
            message=order_msg,
            order=instance,
        )
        send_notification_email(instance.user, "Order Placed Successfully", order_msg)

        # Notify all admins
        notify_admins(
            "order_created",
            "New Order Received",
            f"Order {instance.order_id} placed by {instance.user.username} - {instance.total_amount} DZD. Needs confirmation.",
            order=instance,
        )

    else:
        # Handle status changes
        if instance.status == "confirmed" and instance.confirmed_at:
            # Move to awaiting payment and create invoice
            if not hasattr(instance, "invoice"):
                Order.objects.filter(pk=instance.pk).update(status="awaiting_payment")
                instance.refresh_from_db()

                # Create invoice
                Invoice.objects.create(
                    order=instance,
                    subtotal=instance.subtotal,
                    tax_amount=instance.tax_amount,
                    total_amount=instance.total_amount,
                    status="unpaid",
                )

                # Notify user about confirmation and invoice
                msg = f"Your order {instance.order_id} has been confirmed! Invoice {instance.invoice.invoice_number} is available. Please proceed with payment."
                Notification.objects.create(
                    user=instance.user,
                    notification_type="order_confirmed",
                    title="Order Confirmed",
                    message=msg,
                    order=instance,
                    invoice=instance.invoice,
                )
                send_notification_email(instance.user, "Order Confirmed", msg)

        elif instance.status == "rejected" and instance.rejected_at:
            # Handle rejection
            rejection_note = ""
            if hasattr(instance, "note"):
                rejection_note = f"\n\nReason: {instance.note.content}"

            msg = f"Your order {instance.order_id} has been rejected.{rejection_note}"
            Notification.objects.create(
                user=instance.user,
                notification_type="order_rejected",
                title="Order Rejected",
                message=msg,
                order=instance,
            )
            send_notification_email(instance.user, "Order Rejected", msg)


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
        send_notification_email(order.user, "Payment Proof Submitted", msg)

        # Notify all admins
        notify_admins(
            "payment_submitted",
            "New Payment Proof Submitted",
            f"Payment proof for invoice {invoice.invoice_number} needs review from {order.user.username}.",
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
        send_notification_email(instance.user, "Complaint Submitted", msg)

        # Notify admins
        notify_admins(
            "complaint_created",
            "New Complaint Submitted",
            f"Complaint {instance.complaint_number} from {instance.user.username} - {instance.reason.name if instance.reason else 'Custom'}",
            order=instance.order,
            complaint=instance,
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
