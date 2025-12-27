from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta

from .models import UserProfile, PharmacyProfile, ClinicProfile, DoctorProfile
from .forms import (
    UserRegistrationForm,
    UserProfileForm,
    UserProfileDetailsForm,
    PharmacyProfileForm,
    ClinicProfileForm,
    DoctorProfileForm,
)
from products.models import Wishlist, Product, ProductReview
from payments.models import Order, Cart


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False  # Disable account until admin approval
            user.save()

            # Create user profile
            user_type = form.cleaned_data.get("user_type", "general")
            UserProfile.objects.create(user=user, user_type=user_type)

            # Create specific profile based on user type
            if user_type == "pharmacy":
                PharmacyProfile.objects.create(
                    user=user,
                    pharmacy_name="",
                    license_number="",
                    license_expiry=timezone.now().date(),
                    business_registration="",
                )
            elif user_type == "clinic":
                ClinicProfile.objects.create(
                    user=user,
                    clinic_name="",
                    department="",
                    employee_id="",
                    position="",
                    supervisor_email="",
                )
            elif user_type == "doctor":
                DoctorProfile.objects.create(
                    user=user,
                    medical_license="",
                    specialty="general",
                    years_of_experience=0,
                    hospital_affiliation="",
                    credentials="",
                )

            # Create cart and wishlist
            Cart.objects.create(user=user)
            Wishlist.objects.create(user=user)

            messages.info(
                request,
                "Your account has been created! Please wait for admin approval before logging in.",
            )
            return redirect("accounts:login")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    # Redirect superusers to admin dashboard
    if request.user.is_superuser:
        return redirect("accounts:admin_dashboard")

    # Get or create user profile
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user, user_type="general"
        )

    # Get recent orders
    recent_orders = Order.objects.filter(user=request.user).order_by("-created_at")[:5]

    # Get cart items count
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items_count = cart.get_total_items()
    except Cart.DoesNotExist:
        cart_items_count = 0

    # Get wishlist items count
    try:
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist_items_count = wishlist.products.count()
    except Wishlist.DoesNotExist:
        wishlist_items_count = 0

    # Calculate statistics
    total_orders = Order.objects.filter(user=request.user).count()
    total_spent = (
        Order.objects.filter(
            user=request.user, status__in=["delivered", "shipped"]
        ).aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_activity = {
        "orders": Order.objects.filter(
            user=request.user, created_at__gte=thirty_days_ago
        ).count(),
        "reviews": request.user.productreview_set.filter(
            created_at__gte=thirty_days_ago
        ).count(),
        "questions": request.user.productquestion_set.filter(
            created_at__gte=thirty_days_ago
        ).count(),
    }

    # Role-specific data
    role_specific_data = {}
    if user_profile.user_type == "pharmacy":
        try:
            pharmacy_profile = request.user.pharmacy_profile
            role_specific_data = {
                "pharmacy_name": pharmacy_profile.pharmacy_name,
                "license_number": pharmacy_profile.license_number,
                "verified": pharmacy_profile.verified,
            }
        except PharmacyProfile.DoesNotExist:
            pass
    elif user_profile.user_type == "clinic":
        try:
            clinic_profile = request.user.clinic_profile
            role_specific_data = {
                "clinic_name": clinic_profile.clinic_name,
                "department": clinic_profile.department,
                "budget_limit": clinic_profile.budget_limit,
            }
        except ClinicProfile.DoesNotExist:
            pass
    elif user_profile.user_type == "doctor":
        try:
            doctor_profile = request.user.doctor_profile
            role_specific_data = {
                "specialty": doctor_profile.get_specialty_display(),
                "hospital_affiliation": doctor_profile.hospital_affiliation,
                "verified": doctor_profile.verified,
            }
        except DoctorProfile.DoesNotExist:
            pass

    context = {
        "user_profile": user_profile,
        "recent_orders": recent_orders,
        "cart_items_count": cart_items_count,
        "wishlist_items_count": wishlist_items_count,
        "total_orders": total_orders,
        "total_spent": total_spent,
        "recent_activity": recent_activity,
        "role_specific_data": role_specific_data,
    }

    return render(request, "accounts/dashboard.html", context)


@login_required
def profile(request):
    # Get or create user profile
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user, user_type="general"
        )

    if request.method == "POST":
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = UserProfileDetailsForm(
            request.POST, request.FILES, instance=user_profile
        )

        # Get the appropriate specific profile form
        specific_form = None
        if user_profile.user_type == "pharmacy":
            try:
                pharmacy_profile = request.user.pharmacy_profile
                specific_form = PharmacyProfileForm(
                    request.POST, request.FILES, instance=pharmacy_profile
                )
            except PharmacyProfile.DoesNotExist:
                pass
        elif user_profile.user_type == "clinic":
            try:
                clinic_profile = request.user.clinic_profile
                specific_form = ClinicProfileForm(request.POST, instance=clinic_profile)
            except ClinicProfile.DoesNotExist:
                pass
        elif user_profile.user_type == "doctor":
            try:
                doctor_profile = request.user.doctor_profile
                specific_form = DoctorProfileForm(request.POST, instance=doctor_profile)
            except DoctorProfile.DoesNotExist:
                pass

        forms_valid = user_form.is_valid() and profile_form.is_valid()
        if specific_form:
            forms_valid = forms_valid and specific_form.is_valid()

        if forms_valid:
            user_form.save()
            profile_form.save()
            if specific_form:
                specific_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("accounts:profile")
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = UserProfileDetailsForm(instance=user_profile)

        specific_form = None
        if user_profile.user_type == "pharmacy":
            try:
                specific_form = PharmacyProfileForm(
                    instance=request.user.pharmacy_profile
                )
            except PharmacyProfile.DoesNotExist:
                pass
        elif user_profile.user_type == "clinic":
            try:
                specific_form = ClinicProfileForm(instance=request.user.clinic_profile)
            except ClinicProfile.DoesNotExist:
                pass
        elif user_profile.user_type == "doctor":
            try:
                specific_form = DoctorProfileForm(instance=request.user.doctor_profile)
            except DoctorProfile.DoesNotExist:
                pass

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "specific_form": specific_form,
        "user_profile": user_profile,
    }

    return render(request, "accounts/profile.html", context)


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully!")
            return redirect("accounts:profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def wishlist(request):
    try:
        wishlist = Wishlist.objects.get(user=request.user)
        products = wishlist.products.all()
    except Wishlist.DoesNotExist:
        wishlist = Wishlist.objects.create(user=request.user)
        products = []

    context = {
        "wishlist": wishlist,
        "products": products,
    }

    return render(request, "accounts/wishlist.html", context)


@login_required
def wishlist_remove(request, product_id):
    if request.method == "POST":
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            product = get_object_or_404(Product, id=product_id)
            wishlist.products.remove(product)
            messages.success(
                request, f"{product.name} has been removed from your wishlist."
            )
        except Wishlist.DoesNotExist:
            messages.error(request, "Wishlist not found.")

    return redirect("accounts:wishlist")


# Admin Views
def is_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # User Statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    pending_users = User.objects.filter(is_active=False).count()

    user_type_stats = (
        UserProfile.objects.values("user_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Order Statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="pending").count()
    completed_orders = Order.objects.filter(status="delivered").count()
    total_revenue = (
        Order.objects.filter(status__in=["delivered", "shipped"]).aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    # Product Statistics
    total_products = Product.objects.count()
    out_of_stock = Product.objects.filter(stock_quantity=0).count()
    low_stock = Product.objects.filter(
        stock_quantity__lte=10, stock_quantity__gt=0
    ).count()

    # Recent Orders
    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:10]

    # Monthly Revenue (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_revenue = (
        Order.objects.filter(
            created_at__gte=six_months_ago, status__in=["delivered", "shipped"]
        )
        .extra(select={"month": "strftime('%%Y-%%m', created_at)"})
        .values("month")
        .annotate(revenue=Sum("total_amount"), orders=Count("id"))
        .order_by("month")
    )

    # Top Selling Products
    top_products = Product.objects.annotate(total_sold=Count("orderitem")).order_by(
        "-total_sold"
    )[:5]

    context = {
        "total_users": total_users,
        "active_users": active_users,
        "pending_users": pending_users,
        "user_type_stats": user_type_stats,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_revenue": total_revenue,
        "total_products": total_products,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "recent_orders": recent_orders,
        "monthly_revenue": list(monthly_revenue),
        "top_products": top_products,
    }

    return render(request, "accounts/admin/dashboard.html", context)


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "all")
    user_type_filter = request.GET.get("user_type", "all")

    users = User.objects.select_related("profile").all()

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )

    if status_filter == "active":
        users = users.filter(is_active=True)
    elif status_filter == "inactive":
        users = users.filter(is_active=False)

    if user_type_filter != "all":
        users = users.filter(profile__user_type=user_type_filter)

    users = users.order_by("-date_joined")

    context = {
        "users": users,
        "search_query": search_query,
        "status_filter": status_filter,
        "user_type_filter": user_type_filter,
        "user_types": UserProfile.USER_TYPES,
    }

    return render(request, "accounts/admin/users.html", context)


@login_required
@user_passes_test(is_admin)
def admin_toggle_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.is_active = not user.is_active
        user.save()

        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {status}.")

    return redirect("accounts:admin_users")


@login_required
@user_passes_test(is_admin)
def admin_products_report(request):
    # Product Statistics
    products = (
        Product.objects.select_related("category", "brand")
        .annotate(
            total_sold=Count("orderitem"),
            total_revenue=Sum("orderitem__price"),
            avg_rating=Avg("reviews__rating"),
            review_count=Count("reviews"),
        )
        .order_by("-total_sold")
    )

    # Category Performance
    category_stats = (
        Product.objects.values("category__name")
        .annotate(
            product_count=Count("id"),
            total_revenue=Sum("orderitem__price"),
            avg_price=Avg("price"),
        )
        .order_by("-total_revenue")
    )

    # Specialty Performance
    specialty_stats = (
        Product.objects.values("specialty")
        .annotate(product_count=Count("id"), total_sold=Count("orderitem"))
        .order_by("-total_sold")
    )

    context = {
        "products": products[:20],  # Top 20 products
        "category_stats": category_stats,
        "specialty_stats": specialty_stats,
    }

    return render(request, "accounts/admin/products_report.html", context)


@login_required
@user_passes_test(is_admin)
def admin_stats_api(request):
    """API endpoint for chart data"""
    stat_type = request.GET.get("type", "revenue")

    if stat_type == "revenue":
        # Last 12 months revenue
        twelve_months_ago = timezone.now() - timedelta(days=365)
        data = (
            Order.objects.filter(
                created_at__gte=twelve_months_ago, status__in=["delivered", "shipped"]
            )
            .extra(select={"month": "strftime('%%Y-%%m', created_at)"})
            .values("month")
            .annotate(revenue=Sum("total_amount"))
            .order_by("month")
        )

        return JsonResponse(
            {
                "labels": [item["month"] for item in data],
                "data": [float(item["revenue"]) for item in data],
            }
        )

    elif stat_type == "orders":
        # Orders by status
        data = Order.objects.values("status").annotate(count=Count("id"))

        return JsonResponse(
            {
                "labels": [item["status"].title() for item in data],
                "data": [item["count"] for item in data],
            }
        )

    elif stat_type == "users":
        # Users by type
        data = UserProfile.objects.values("user_type").annotate(count=Count("id"))

        return JsonResponse(
            {
                "labels": [
                    dict(UserProfile.USER_TYPES).get(item["user_type"]) for item in data
                ],
                "data": [item["count"] for item in data],
            }
        )

    return JsonResponse({"error": "Invalid type"}, status=400)
