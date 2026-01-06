from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import FAQ, Testimonial, SiteInformation, TeamMember
from .forms import ContactForm
from products.models import Product, Category


def index(request):
    # Get featured and trending products
    featured_products = Product.objects.filter(featured=True)[:8]
    trending_products = Product.objects.filter(trending=True)[:6]
    testimonials = Testimonial.objects.filter(is_featured=True)[:6]
    categories = Category.objects.all()
    print(f"settings.EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"settings.EMAIL_HOST_PASSWORD: {settings.EMAIL_HOST_PASSWORD}")
    context = {
        "featured_products": featured_products,
        "trending_products": trending_products,
        "testimonials": testimonials,
        "categories": categories,
    }
    return render(request, "pages/index.html", context)


def about(request):
    team_members = TeamMember.objects.filter(is_active=True, show_on_about_page=True)

    context = {
        "team_members": team_members,
    }
    return render(request, "pages/about.html", context)


def contact(request):
    site_info = SiteInformation.get_instance()

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()

            # Send email notification to admin
            try:
                admin_message = f"""
New Contact Message Received

Name: {contact_message.name}
Email: {contact_message.email}
Phone: {contact_message.phone}
Inquiry Type: {contact_message.get_inquiry_type_display()}

Message:
{contact_message.message}

Reply to: {contact_message.email}
                """

                send_mail(
                    subject=f"New Contact Message: {contact_message.subject}",
                    message=admin_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[site_info.email],
                    fail_silently=True,
                )

                # Send confirmation email to user
                user_message = f"""
Dear {contact_message.name},

Thank you for contacting us! We have received your message and will get back to you as soon as possible.

Your Message Details:
Subject: {contact_message.subject}
Inquiry Type: {contact_message.get_inquiry_type_display()}

Your Message:
{contact_message.message}

Best regards,
{site_info.site_name}
                """

                send_mail(
                    subject=f"Message Received: {contact_message.subject}",
                    message=user_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[contact_message.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(
                request,
                "Your message has been sent successfully! We will get back to you soon.",
            )
            return redirect("pages:contact")
    else:
        form = ContactForm()

    context = {
        "form": form,
    }
    return render(request, "pages/contact.html", context)


def faq(request):
    faqs_by_category = {}
    faqs = FAQ.objects.filter(is_active=True).order_by("category", "order")

    for faq in faqs:
        category = faq.get_category_display()
        if category not in faqs_by_category:
            faqs_by_category[category] = []
        faqs_by_category[category].append(faq)

    return render(request, "pages/faq.html", {"faqs_by_category": faqs_by_category})
