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
    """Notifier tous les utilisateurs administrateurs actifs par notification et email"""
    admin_users = User.objects.filter(is_staff=True, is_active=True)
    for admin in admin_users:
        # Créer notification dans la base de données
        Notification.objects.create(
            user=admin,
            notification_type=notification_type,
            title=title,
            message=message,
            **related_objects,
        )
        # Envoyer notification par email
        send_notification_email(admin, title, message)


def send_notification_email(user, title, message):
    """Fonction d'aide pour envoyer des notifications par email"""
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
    """Gérer la création de commande et les changements de statut"""
    if created:
        # Notifier l'utilisateur de la création de commande
        order_msg = f"Votre commande {instance.order_id} a été passée et est en attente de confirmation."
        Notification.objects.create(
            user=instance.user,
            notification_type="order_created",
            title="Commande passée avec succès",
            message=order_msg,
            order=instance,
        )
        send_notification_email(instance.user, "Commande passée avec succès", order_msg)

        # Notifier tous les administrateurs
        notify_admins(
            "order_created",
            "Nouvelle commande reçue",
            f"Commande {instance.order_id} passée par {instance.user.username} - {instance.total_amount} DZD. Nécessite confirmation.",
            order=instance,
        )

    else:
        # Gérer les changements de statut
        if instance.status == "confirmed" and instance.confirmed_at:
            # Passer à en attente de paiement et créer la facture
            if not hasattr(instance, "invoice"):
                Order.objects.filter(pk=instance.pk).update(status="awaiting_payment")
                instance.refresh_from_db()

                # Créer la facture
                Invoice.objects.create(
                    order=instance,
                    subtotal=instance.subtotal,
                    tax_amount=instance.tax_amount,
                    total_amount=instance.total_amount,
                    status="unpaid",
                )

                # Notifier l'utilisateur de la confirmation et de la facture
                msg = f"Votre commande {instance.order_id} a été confirmée ! La facture {instance.invoice.invoice_number} est disponible. Veuillez procéder au paiement."
                Notification.objects.create(
                    user=instance.user,
                    notification_type="order_confirmed",
                    title="Commande confirmée",
                    message=msg,
                    order=instance,
                    invoice=instance.invoice,
                )
                send_notification_email(instance.user, "Commande confirmée", msg)

        elif instance.status == "rejected" and instance.rejected_at:
            # Gérer le rejet
            rejection_note = ""
            if hasattr(instance, "note"):
                rejection_note = f"\n\nMotif : {instance.note.content}"

            msg = f"Votre commande {instance.order_id} a été rejetée.{rejection_note}"
            Notification.objects.create(
                user=instance.user,
                notification_type="order_rejected",
                title="Commande rejetée",
                message=msg,
                order=instance,
            )
            send_notification_email(instance.user, "Commande rejetée", msg)


@receiver(post_save, sender=PaymentProof)
def update_invoice_on_payment_proof(sender, instance, created, **kwargs):
    """Mettre à jour le statut de la facture lors du téléchargement de la preuve de paiement"""
    if created:
        invoice = instance.invoice
        invoice.status = "payment_submitted"
        invoice.save()

        # Mettre à jour le statut de la commande
        order = invoice.order
        order.status = "payment_under_review"
        order.save()

        # Notifier l'utilisateur
        msg = f"Votre preuve de paiement pour la facture {invoice.invoice_number} est en cours de vérification."
        Notification.objects.create(
            user=order.user,
            notification_type="payment_submitted",
            title="Preuve de paiement soumise",
            message=msg,
            order=order,
            invoice=invoice,
        )
        send_notification_email(order.user, "Preuve de paiement soumise", msg)

        # Notifier tous les administrateurs
        notify_admins(
            "payment_submitted",
            "Nouvelle preuve de paiement soumise",
            f"Preuve de paiement pour la facture {invoice.invoice_number} nécessite vérification de {order.user.username}.",
            order=order,
            invoice=invoice,
        )


@receiver(post_save, sender=PaymentProof)
def handle_payment_verification(sender, instance, created, **kwargs):
    """Gérer la vérification du paiement (approuver/rejeter)"""
    if not created and instance.verified:
        invoice = instance.invoice
        order = invoice.order

        # Mettre à jour la facture
        invoice.status = "paid"
        invoice.paid_at = instance.verified_at or timezone.now()
        invoice.save()

        # Mettre à jour la commande
        order.status = "paid"
        order.paid_at = invoice.paid_at
        order.save()

        # Créer le reçu de paiement
        if not hasattr(invoice, "receipt"):
            PaymentReceipt.objects.create(
                invoice=invoice,
                payment_proof=instance,
                amount_paid=invoice.total_amount,
                payment_date=invoice.paid_at,
                payment_method=instance.payment_method,
            )

        # Notifier l'utilisateur
        msg = f"Votre paiement pour la facture {invoice.invoice_number} a été confirmé. Le reçu est maintenant disponible."
        Notification.objects.create(
            user=order.user,
            notification_type="payment_confirmed",
            title="Paiement confirmé",
            message=msg,
            order=order,
            invoice=invoice,
        )
        send_notification_email(order.user, "Paiement confirmé", msg)

    elif not created and instance.rejection_reason:
        invoice = instance.invoice
        invoice.status = "payment_rejected"
        invoice.save()

        order = invoice.order
        msg = f"Votre preuve de paiement pour la facture {invoice.invoice_number} a été rejetée. Motif : {instance.rejection_reason}"

        Notification.objects.create(
            user=order.user,
            notification_type="payment_rejected",
            title="Paiement rejeté",
            message=msg,
            order=order,
            invoice=invoice,
        )
        send_notification_email(order.user, "Paiement rejeté", msg)


@receiver(post_save, sender=Complaint)
def notify_on_complaint(sender, instance, created, **kwargs):
    """Créer une notification lors de la création ou mise à jour d'une réclamation"""
    if created:
        msg = f"Votre réclamation {instance.complaint_number} a été soumise et est en cours d'examen."
        Notification.objects.create(
            user=instance.user,
            notification_type="complaint_created",
            title="Réclamation soumise",
            message=msg,
            order=instance.order,
            complaint=instance,
        )
        send_notification_email(instance.user, "Réclamation soumise", msg)

        # Notifier les administrateurs
        notify_admins(
            "complaint_created",
            "Nouvelle réclamation soumise",
            f"Réclamation {instance.complaint_number} de {instance.user.username} - {instance.reason.name if instance.reason else 'Personnalisé'}",
            order=instance.order,
            complaint=instance,
        )
    else:
        # Changement de statut
        if instance.status == "resolved":
            msg = f"Votre réclamation {instance.complaint_number} a été résolue."
            title = "Réclamation résolue"
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
            msg = f"Votre réclamation {instance.complaint_number} statut : {instance.get_status_display()}"
            title = "Réclamation mise à jour"
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
    """Notifier l'utilisateur des changements de statut de remboursement"""
    if created:
        msg = f"Un remboursement de {instance.amount} DZD a été initié pour la commande {instance.order.order_id}."
        Notification.objects.create(
            user=instance.order.user,
            notification_type="refund_initiated",
            title="Remboursement initié",
            message=msg,
            order=instance.order,
            refund=instance,
        )
        send_notification_email(instance.order.user, "Remboursement initié", msg)

        # Notifier les autres administrateurs
        notify_admins(
            "refund_initiated",
            "Remboursement approuvé",
            f"Remboursement {instance.refund_number} approuvé pour la commande {instance.order.order_id} - {instance.amount} DZD",
            order=instance.order,
            refund=instance,
        )


@receiver(post_save, sender=RefundProof)
def complete_refund_on_proof(sender, instance, created, **kwargs):
    """Finaliser le remboursement lors du téléchargement de la preuve"""
    if created:
        refund = instance.refund
        refund.status = "refund_completed"
        refund.completed_at = timezone.now()
        refund.save()

        # Mettre à jour la commande
        order = refund.order
        order.status = "refunded"
        order.save()

        # Mettre à jour la facture
        invoice = refund.invoice
        invoice.status = "refunded"
        invoice.save()

        # Créer le reçu de remboursement
        if not hasattr(refund, "receipt"):
            RefundReceipt.objects.create(
                refund=refund,
                refund_proof=instance,
                amount_refunded=refund.amount,
                refund_date=refund.completed_at,
                refund_method=refund.refund_method,
            )

        # Notifier l'utilisateur
        msg = f"Votre remboursement de {refund.amount} DZD a été effectué. Le reçu est disponible."
        Notification.objects.create(
            user=order.user,
            notification_type="refund_completed",
            title="Remboursement effectué",
            message=msg,
            order=order,
            refund=refund,
        )
        send_notification_email(order.user, "Remboursement effectué", msg)
