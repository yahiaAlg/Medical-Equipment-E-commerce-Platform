from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Min, Max
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
import json

from .models import Product, Category, Brand, ProductReview, ProductQuestion, Wishlist
from .forms import ProductReviewForm, ProductQuestionForm


from django.db.models import Avg
from django.core.paginator import Paginator


def product_list(request):
    # Base queryset with optimized related data fetching
    products = (
        Product.objects.all()
        .select_related("brand")
        .prefetch_related("images", "categories")
    )

    # Fetch all categories and brands for context
    categories = Category.objects.all()
    brands = Brand.objects.all()

    # Calculate price range from all products
    price_stats = Product.objects.aggregate(
        min_price=Min("price"), max_price=Max("price")
    )
    min_price_all = price_stats["min_price"] or 0
    max_price_all = price_stats["max_price"] or 1000

    # Calculate dynamic step (1% of range, minimum 1)
    price_range = max_price_all - min_price_all
    price_step = max(1, round(price_range / 100))

    # Get filter and sort parameters from request
    category_filter = request.GET.get("category")
    brand_filter = request.GET.get("brand")
    specialty_filter = request.GET.get("specialty")
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    availability = request.GET.get("availability")
    sort_by = request.GET.get("sort", "name")

    # Apply filters
    if category_filter:
        products = products.filter(categories__slug=category_filter)
    if brand_filter:
        products = products.filter(brand_id=brand_filter)
    if specialty_filter:
        products = products.filter(specialty=specialty_filter)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if availability:
        products = products.filter(availability_status=availability)

    # Apply sorting
    if sort_by == "price_low":
        products = products.order_by("price")
    elif sort_by == "price_high":
        products = products.order_by("-price")
    elif sort_by == "newest":
        products = products.order_by("-created_at")
    elif sort_by == "rating":
        products = products.annotate(avg_rating=Avg("reviews__rating")).order_by(
            "-avg_rating"
        )
    else:
        products = products.order_by("name")

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Context for template
    context = {
        "page_obj": page_obj,
        "categories": categories,
        "brands": brands,
        "current_filters": {
            "category": category_filter,
            "brand": brand_filter,
            "specialty": specialty_filter,
            "price_min": price_min,
            "price_max": price_max,
            "availability": availability,
            "sort": sort_by,
        },
        "specialties": Product.SPECIALTIES,
        "availability_choices": Product.AVAILABILITY_STATUS,
        "min_price_all": min_price_all,
        "max_price_all": max_price_all,
        "price_step": price_step,
    }

    return render(request, "products/list.html", context)


def specialty_list(request):
    """Display all categories as specialties"""
    categories = Category.objects.all().prefetch_related("products")

    context = {
        "categories": categories,
    }

    return render(request, "products/specialties.html", context)


def search(request):
    query = request.GET.get("q", "")
    products = Product.objects.none()

    if query:
        products = (
            Product.objects.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(short_description__icontains=query)
                | Q(brand__name__icontains=query)
                | Q(categories__name__icontains=query)  # Supports multiple categories
            )
            .select_related("brand")
            .prefetch_related("images", "categories")
            .distinct()
        )

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
        "total_results": products.count(),
    }

    return render(request, "products/search_results.html", context)


def category_detail(request, slug):
    """Redirect to product list with category filter"""
    return redirect(f"{reverse('products:list')}?category={slug}")


def product_detail(request, slug):
    # Fetch the product with prefetched categories
    product = get_object_or_404(
        Product.objects.prefetch_related("categories", "variants"), slug=slug
    )

    # Fetch related products (matching any of the product's categories)
    related_products = (
        Product.objects.filter(categories__in=product.categories.all())
        .exclude(id=product.id)
        .distinct()[:4]
    )

    # Fetch reviews and questions with optimized queries
    reviews = ProductReview.objects.filter(product=product).select_related("user")
    questions = ProductQuestion.objects.filter(product=product).select_related(
        "user", "answered_by"
    )

    # Get active variants
    variants = product.variants.filter(is_active=True)

    # Calculate review statistics
    review_stats = reviews.aggregate(avg_rating=Avg("rating"), total_count=Count("id"))

    # Get rating distribution
    rating_distribution = {i: 0 for i in range(1, 6)}
    for rating in reviews.values("rating").annotate(count=Count("rating")):
        rating_distribution[rating["rating"]] = rating["count"]

    # Calculate percentages for rating bars
    total_reviews = review_stats["total_count"] or 0
    rating_percentages = {
        star: (count / total_reviews * 100) if total_reviews > 0 else 0
        for star, count in rating_distribution.items()
    }

    # Check wishlist status
    in_wishlist = False
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        in_wishlist = wishlist.products.filter(id=product.id).exists()
        wishlist_product_ids = list(wishlist.products.values_list("id", flat=True))

    # Prepare context for template
    context = {
        "product": product,
        "reviews": reviews,
        "questions": questions,
        "related_products": related_products,
        "variants": variants,
        "in_wishlist": in_wishlist,
        "wishlist_product_ids": wishlist_product_ids,
        "review_stats": review_stats,
        "rating_distribution": rating_distribution,
        "rating_percentages": rating_percentages,
        "review_form": ProductReviewForm(),
        "question_form": ProductQuestionForm(),
    }

    return render(request, "products/detail.html", context)


@login_required
def toggle_wishlist(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")

        try:
            product = Product.objects.get(id=product_id)
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)

            if wishlist.products.filter(id=product_id).exists():
                wishlist.products.remove(product)
                added = False
            else:
                wishlist.products.add(product)
                added = True

            return JsonResponse(
                {
                    "success": True,
                    "added": added,
                    "in_wishlist": added,
                    "message": (
                        "Added to wishlist" if added else "Removed from wishlist"
                    ),
                }
            )
        except Product.DoesNotExist:
            return JsonResponse({"success": False, "message": "Product not found"})

    return JsonResponse({"success": False, "message": "Invalid request"})


def send_admin_notification(subject, message):
    """Send email notification to all superusers"""
    try:
        admin_emails = list(
            User.objects.filter(is_superuser=True).values_list("email", flat=True)
        )
        if admin_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=True,
            )
    except Exception as e:
        print(f"Error sending admin notification: {e}")


@login_required
def add_review(request):
    if request.method == "POST":
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            product_id = request.POST.get("product_id")
            try:
                product = Product.objects.get(id=product_id)

                # Check if user already reviewed this product
                existing_review = ProductReview.objects.filter(
                    product=product, user=request.user
                ).first()

                if existing_review:
                    messages.error(request, "You have already reviewed this product.")
                else:
                    review = form.save(commit=False)
                    review.product = product
                    review.user = request.user
                    review.save()
                    messages.success(
                        request, "Your review has been added successfully!"
                    )

                    # Send email to admins
                    send_admin_notification(
                        subject=f"New Review: {product.name}",
                        message=f"User {request.user.username} posted a new review:\n\n"
                        f"Product: {product.name}\n"
                        f"Rating: {review.rating} stars\n"
                        f"Title: {review.title}\n"
                        f"Comment: {review.comment}\n\n"
                        f"View product: {request.build_absolute_uri(product.get_absolute_url())}",
                    )

            except Product.DoesNotExist:
                messages.error(request, "Product not found.")

        return redirect("products:detail", slug=request.POST.get("product_slug"))

    return redirect("products:list")


@login_required
def ask_question(request):
    if request.method == "POST":
        form = ProductQuestionForm(request.POST)
        if form.is_valid():
            product_id = request.POST.get("product_id")
            try:
                product = Product.objects.get(id=product_id)
                question = form.save(commit=False)
                question.product = product
                question.user = request.user
                question.save()
                messages.success(
                    request, "Your question has been submitted successfully!"
                )

                # Send email to admins
                send_admin_notification(
                    subject=f"New Question: {product.name}",
                    message=f"User {request.user.username} asked a question:\n\n"
                    f"Product: {product.name}\n"
                    f"Question: {question.question}\n\n"
                    f"View product: {request.build_absolute_uri(product.get_absolute_url())}",
                )

            except Product.DoesNotExist:
                messages.error(request, "Product not found.")

        return redirect("products:detail", slug=request.POST.get("product_slug"))

    return redirect("products:list")
