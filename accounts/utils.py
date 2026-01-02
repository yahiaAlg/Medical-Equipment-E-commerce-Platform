from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime
from pages.models import SiteInformation


def send_account_status_email(user, is_active):
    """
    Send an email notification when user account status is toggled

    Args:
        user: User object
        is_active: Boolean indicating if account is now active
    """
    # Get site information
    site_info = SiteInformation.get_instance()

    # Determine which template to use
    template_name = (
        "emails/account_activated.html"
        if is_active
        else "emails/account_deactivated.html"
    )
    subject = f'{site_info.site_name} - Your Account Has Been {"Activated" if is_active else "Deactivated"}'

    # Context for the email template
    context = {
        "user": user,
        "site_info": site_info,
        "site_url": getattr(settings, "SITE_URL", "http://localhost:8000"),
        "current_year": datetime.now().year,
    }

    # Render HTML content
    html_message = render_to_string(template_name, context)

    # Create plain text version (fallback)
    plain_message = strip_tags(html_message)

    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=(
                site_info.email if site_info.email else settings.DEFAULT_FROM_EMAIL
            ),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error in production
        print(f"Error sending email: {str(e)}")
        return False
