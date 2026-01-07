from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from payments.models import Notification
from products.models import ProductReview, ProductQuestion
from pages.models import ContactMessage


def notify_admins(notification_type, title, message, **extra_data):
    """Notifier tous les administrateurs actifs"""
    admin_users = User.objects.filter(is_staff=True, is_active=True)
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            notification_type=notification_type,
            title=title,
            message=message,
            **extra_data,
        )


def send_notification_email(user, title, message):
    """Fonction auxiliaire pour envoyer des emails de notification"""
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


@receiver(post_save, sender=User)
def notify_on_user_registration(sender, instance, created, **kwargs):
    """Notifier les administrateurs lors de l'inscription d'un nouvel utilisateur"""
    if created and not instance.is_staff:
        title = "Nouvel utilisateur inscrit"
        message = f"Le nouvel utilisateur {instance.username} ({instance.email}) s'est inscrit."

        notify_admins(notification_type="user_registered", title=title, message=message)

        # Envoyer un email aux administrateurs
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin in admin_users:
            send_notification_email(admin, title, message)


@receiver(post_save, sender=ProductReview)
def notify_on_review_submission(sender, instance, created, **kwargs):
    """Notifier les administrateurs lors de la soumission d'un nouvel avis"""
    if created:
        title = "Nouvel avis produit"
        message = f"{instance.user.username} a évalué {instance.product.name} - {instance.rating} étoiles"

        notify_admins(
            notification_type="review_submitted", title=title, message=message
        )

        # Envoyer un email aux administrateurs
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin in admin_users:
            send_notification_email(admin, title, message)


@receiver(post_save, sender=ProductQuestion)
def notify_on_question_submission(sender, instance, created, **kwargs):
    """Notifier les administrateurs lors de la soumission d'une nouvelle question"""
    if created:
        title = "Nouvelle question produit"
        message = f"{instance.user.username} a posé une question sur {instance.product.name}: {instance.question[:50]}..."

        notify_admins(
            notification_type="question_submitted", title=title, message=message
        )

        # Envoyer un email aux administrateurs
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin in admin_users:
            send_notification_email(admin, title, message)


@receiver(post_save, sender=ContactMessage)
def notify_on_contact_message(sender, instance, created, **kwargs):
    """Notifier les administrateurs lors de la réception d'un nouveau message de contact"""
    if created:
        title = "Nouveau message de contact"
        message = f"{instance.name} ({instance.email}) a envoyé un message de type {instance.get_inquiry_type_display()}: {instance.subject}"

        notify_admins(notification_type="contact_message", title=title, message=message)

        # Envoyer un email aux administrateurs
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin in admin_users:
            send_notification_email(admin, title, message)
