from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
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
        Notification.objects.create(
            user=instance.user,
            notification_type="order_created",
            title="Order Placed Successfully",
            message=f"Your order {instance.order_id} has been placed. Invoice has been generated.",
            order=instance,
        )

        # Create notification for invoice
        Notification.objects.create(
            user=instance.user,
            notification_type="invoice_created",
            title="Invoice Generated",
            message=f"Invoice {instance.invoice.invoice_number} is now available. Please make payment and upload proof.",
            order=instance,
            invoice=instance.invoice,
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
        Notification.objects.create(
            user=order.user,
            notification_type="payment_submitted",
            title="Payment Proof Submitted",
            message=f"Your payment proof for invoice {invoice.invoice_number} is under review.",
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
        Notification.objects.create(
            user=order.user,
            notification_type="payment_confirmed",
            title="Payment Confirmed",
            message=f"Your payment for invoice {invoice.invoice_number} has been confirmed. Receipt is now available.",
            order=order,
            invoice=invoice,
        )

    elif not created and instance.rejection_reason:
        invoice = instance.invoice
        invoice.status = "payment_rejected"
        invoice.save()

        order = invoice.order

        Notification.objects.create(
            user=order.user,
            notification_type="payment_rejected",
            title="Payment Rejected",
            message=f"Your payment proof for invoice {invoice.invoice_number} was rejected. Reason: {instance.rejection_reason}",
            order=order,
            invoice=invoice,
        )


@receiver(post_save, sender=Complaint)
def notify_on_complaint(sender, instance, created, **kwargs):
    """Create notification when complaint is created or updated"""
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type="complaint_created",
            title="Complaint Submitted",
            message=f"Your complaint {instance.complaint_number} has been submitted and is being reviewed.",
            order=instance.order,
            complaint=instance,
        )
    else:
        # Status changed
        if instance.status == "resolved":
            Notification.objects.create(
                user=instance.user,
                notification_type="complaint_resolved",
                title="Complaint Resolved",
                message=f"Your complaint {instance.complaint_number} has been resolved.",
                order=instance.order,
                complaint=instance,
            )
        else:
            Notification.objects.create(
                user=instance.user,
                notification_type="complaint_updated",
                title="Complaint Updated",
                message=f"Your complaint {instance.complaint_number} status: {instance.get_status_display()}",
                order=instance.order,
                complaint=instance,
            )


@receiver(post_save, sender=Refund)
def notify_on_refund(sender, instance, created, **kwargs):
    """Notify user about refund status changes"""
    if created:
        Notification.objects.create(
            user=instance.order.user,
            notification_type="refund_initiated",
            title="Refund Initiated",
            message=f"A refund of {instance.amount} DZD has been initiated for order {instance.order.order_id}.",
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
        Notification.objects.create(
            user=order.user,
            notification_type="refund_completed",
            title="Refund Completed",
            message=f"Your refund of {refund.amount} DZD has been completed. Receipt is available.",
            order=order,
            refund=refund,
        )
