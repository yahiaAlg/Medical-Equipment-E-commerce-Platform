from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from payments.models import Notification
from products.models import ProductReview, ProductQuestion
from pages.models import ContactMessage


def notify_admins(notification_type, title, message, **extra_data):
    """Notify all active admin users"""
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


@receiver(post_save, sender=User)
def notify_on_user_registration(sender, instance, created, **kwargs):
    """Notify admins when a new user registers"""
    if created and not instance.is_staff:
        title = "New User Registered"
        message = f"New user {instance.username} ({instance.email}) has registered."

        notify_admins(notification_type="user_registered", title=title, message=message)

        # Send email to admins
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin in admin_users:
            send_notification_email(admin, title, message)


@receiver(post_save, sender=ProductReview)
def notify_on_review_submission(sender, instance, created, **kwargs):
    """Notify admins when a new review is submitted"""
    if created:
        title = "New Product Review"
        message = f"{instance.user.username} reviewed {instance.product.name} - {instance.rating} stars"

        notify_admins(
            notification_type="review_submitted", title=title, message=message
        )

        # Send email to admins
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin in admin_users:
            send_notification_email(admin, title, message)


@receiver(post_save, sender=ProductQuestion)
def notify_on_question_submission(sender, instance, created, **kwargs):
    """Notify admins when a new question is submitted"""
    if created:
        title = "New Product Question"
        message = f"{instance.user.username} asked about {instance.product.name}: {instance.question[:50]}..."

        notify_admins(
            notification_type="question_submitted", title=title, message=message
        )

        # Send email to admins
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin in admin_users:
            send_notification_email(admin, title, message)


@receiver(post_save, sender=ContactMessage)
def notify_on_contact_message(sender, instance, created, **kwargs):
    """Notify admins when a new contact message is received"""
    if created:
        title = "New Contact Message"
        message = f"{instance.name} ({instance.email}) sent a {instance.get_inquiry_type_display()} message: {instance.subject}"

        notify_admins(notification_type="contact_message", title=title, message=message)

        # Send email to admins
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        for admin in admin_users:
            send_notification_email(admin, title, message)
