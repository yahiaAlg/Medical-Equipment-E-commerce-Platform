from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import FAQ, Testimonial, ContactMessage
from .forms import ContactForm
from products.models import Product, Category

def index(request):
    # Get featured and trending products
    featured_products = Product.objects.filter(featured=True)[:8]
    trending_products = Product.objects.filter(trending=True)[:6]
    testimonials = Testimonial.objects.filter(is_featured=True)[:6]
    categories = Category.objects.all()[:6]
    
    context = {
        'featured_products': featured_products,
        'trending_products': trending_products,
        'testimonials': testimonials,
        'categories': categories,
    }
    return render(request, 'pages/index.html', context)

def about(request):
    return render(request, 'pages/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            
            # Send email notification
            try:
                send_mail(
                    subject=f'New Contact Message: {contact_message.subject}',
                    message=f'''
                    Name: {contact_message.name}
                    Email: {contact_message.email}
                    Phone: {contact_message.phone}
                    Inquiry Type: {contact_message.get_inquiry_type_display()}
                    
                    Message:
                    {contact_message.message}
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['admin@medequippro.com'],
                    fail_silently=True,
                )
            except Exception:
                pass
            
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('pages:contact')
    else:
        form = ContactForm()
    
    return render(request, 'pages/contact.html', {'form': form})

def faq(request):
    faqs_by_category = {}
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    
    for faq in faqs:
        category = faq.get_category_display()
        if category not in faqs_by_category:
            faqs_by_category[category] = []
        faqs_by_category[category].append(faq)
    
    return render(request, 'pages/faq.html', {'faqs_by_category': faqs_by_category})