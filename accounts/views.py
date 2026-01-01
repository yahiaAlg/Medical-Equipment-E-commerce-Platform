import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from django.db.models import Sum, Count, Avg, F, Q, DecimalField
from django.db.models.functions import TruncDate

from .models import *
from .forms import (
    UserRegistrationForm,
    UserProfileForm,
    UserProfileDetailsForm,
    PharmacyProfileForm,
    ClinicProfileForm,
    DoctorProfileForm,
)
from pages.models import ContactMessage
from products.models import *
from payments.models import *


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
        form_type = request.POST.get("form_type")

        # Handle password change form
        if form_type == "password":
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(
                    request, "Your password has been changed successfully!"
                )
                return redirect("accounts:profile")
            else:
                # Initialize other forms for display
                user_form = UserProfileForm(instance=request.user)
                profile_form = UserProfileDetailsForm(instance=user_profile)
                specific_form = get_specific_profile_form(user_profile, None)

        # Handle profile update form
        else:
            user_form = UserProfileForm(request.POST, instance=request.user)
            profile_form = UserProfileDetailsForm(
                request.POST, request.FILES, instance=user_profile
            )

            specific_form = get_specific_profile_form(
                user_profile, request.POST, request.FILES
            )

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

            # Initialize password form for display
            password_form = PasswordChangeForm(request.user)
    else:
        # Initialize all forms for GET request
        user_form = UserProfileForm(instance=request.user)
        profile_form = UserProfileDetailsForm(instance=user_profile)
        password_form = PasswordChangeForm(request.user)
        specific_form = get_specific_profile_form(user_profile, None)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "password_form": password_form,
        "specific_form": specific_form,
        "user_profile": user_profile,
    }

    return render(request, "accounts/profile.html", context)


def get_specific_profile_form(user_profile, post_data=None, files=None):
    """Helper function to get the appropriate specific profile form"""
    specific_form = None

    if user_profile.user_type == "pharmacy":
        try:
            pharmacy_profile = user_profile.user.pharmacy_profile
            if post_data:
                specific_form = PharmacyProfileForm(
                    post_data, files, instance=pharmacy_profile
                )
            else:
                specific_form = PharmacyProfileForm(instance=pharmacy_profile)
        except PharmacyProfile.DoesNotExist:
            pass

    elif user_profile.user_type == "clinic":
        try:
            clinic_profile = user_profile.user.clinic_profile
            if post_data:
                specific_form = ClinicProfileForm(post_data, instance=clinic_profile)
            else:
                specific_form = ClinicProfileForm(instance=clinic_profile)
        except ClinicProfile.DoesNotExist:
            pass

    elif user_profile.user_type == "doctor":
        try:
            doctor_profile = user_profile.user.doctor_profile
            if post_data:
                specific_form = DoctorProfileForm(post_data, instance=doctor_profile)
            else:
                specific_form = DoctorProfileForm(instance=doctor_profile)
        except DoctorProfile.DoesNotExist:
            pass

    return specific_form


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
    # Get or create wishlist
    try:
        wishlist = Wishlist.objects.get(user=request.user)
    except Wishlist.DoesNotExist:
        wishlist = Wishlist.objects.create(user=request.user)

    # Get all products with additional data
    products = wishlist.products.annotate(
        average_rating=Avg("reviews__rating"), review_count=Count("reviews")
    ).select_related("brand", "category")

    context = {
        "wishlist": wishlist,
        "products": products,
    }

    return render(request, "accounts/wishlist.html", context)


@login_required
def wishlist_add(request, product_id):
    """Add product to wishlist"""
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        try:
            wishlist = Wishlist.objects.get(user=request.user)
        except Wishlist.DoesNotExist:
            wishlist = Wishlist.objects.create(user=request.user)

        if product in wishlist.products.all():
            messages.info(request, f"{product.name} is already in your wishlist.")
        else:
            wishlist.products.add(product)
            messages.success(
                request, f"{product.name} has been added to your wishlist."
            )

    # Redirect back to the previous page or product detail
    return redirect(request.META.get("HTTP_REFERER", "products:list"))


@login_required
def wishlist_remove(request, product_id):
    """Remove product from wishlist"""
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


@login_required
def wishlist_toggle(request, product_id):
    """Toggle product in wishlist (add if not present, remove if present)"""
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        try:
            wishlist = Wishlist.objects.get(user=request.user)
        except Wishlist.DoesNotExist:
            wishlist = Wishlist.objects.create(user=request.user)

        if product in wishlist.products.all():
            wishlist.products.remove(product)
            messages.success(
                request, f"{product.name} has been removed from your wishlist."
            )
        else:
            wishlist.products.add(product)
            messages.success(
                request, f"{product.name} has been added to your wishlist."
            )

    # Return JSON for AJAX requests
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        from django.http import JsonResponse

        return JsonResponse(
            {"success": True, "in_wishlist": product in wishlist.products.all()}
        )

    return redirect(request.META.get("HTTP_REFERER", "products:list"))


# ========== ADMIN VIEWS ==========


def is_admin(user):
    return user.is_superuser


def is_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard with all management sections"""
    tab = request.GET.get("tab", "overview")

    # Overview statistics
    stats = {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "pending_approvals": User.objects.filter(is_active=False).count(),
        "total_orders": Order.objects.count(),
        "pending_payments": PaymentProof.objects.filter(verified=False).count(),
        "open_complaints": Complaint.objects.filter(status="open").count(),
        "pending_refunds": Refund.objects.filter(status="refund_pending").count(),
    }

    # Recent activity
    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:5]
    recent_users = User.objects.order_by("-date_joined")[:5]
    pending_payments = PaymentProof.objects.filter(verified=False).select_related(
        "invoice__order__user"
    )[:5]

    context = {
        "tab": tab,
        "stats": stats,
        "recent_orders": recent_orders,
        "recent_users": recent_users,
        "pending_payments": pending_payments,
    }

    return render(request, "accounts/admin/dashboard.html", context)


@login_required
@user_passes_test(is_admin)
def admin_users_management(request):
    """User management section"""
    status_filter = request.GET.get("status", "all")
    user_type_filter = request.GET.get("user_type", "all")
    search = request.GET.get("search", "")

    users = User.objects.select_related("profile").all()

    if status_filter == "active":
        users = users.filter(is_active=True)
    elif status_filter == "inactive":
        users = users.filter(is_active=False)
    elif status_filter == "pending":
        users = users.filter(is_active=False, is_superuser=False)

    if user_type_filter != "all":
        users = users.filter(profile__user_type=user_type_filter)

    if search:
        users = users.filter(
            Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
        )

    users = users.order_by("-date_joined")

    context = {
        "users": users,
        "status_filter": status_filter,
        "user_type_filter": user_type_filter,
        "search": search,
    }

    return render(request, "accounts/admin/users_management.html", context)


@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """View and edit user details"""
    user = get_object_or_404(User, id=user_id)
    user_profile = user.profile

    # Get user statistics
    total_orders = Order.objects.filter(user=user).count()
    total_spent = (
        Order.objects.filter(user=user, status__in=["delivered", "shipped"]).aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    orders = Order.objects.filter(user=user).order_by("-created_at")[:10]

    context = {
        "user_obj": user,
        "user_profile": user_profile,
        "total_orders": total_orders,
        "total_spent": total_spent,
        "orders": orders,
    }

    return render(request, "accounts/admin/user_detail.html", context)


@login_required
@user_passes_test(is_admin)
def admin_toggle_user_status(request, user_id):
    """Toggle user active status"""
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()

        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {status}.")

        return JsonResponse({"success": True, "is_active": user.is_active})

    return JsonResponse({"success": False})


@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    """Delete user account"""
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)

        if user.is_superuser:
            messages.error(request, "Cannot delete superuser accounts.")
            return redirect("accounts:admin_users_management")

        username = user.username
        user.delete()
        messages.success(request, f"User {username} has been deleted.")

    return redirect("accounts:admin_users_management")


@login_required
@user_passes_test(is_admin)
def admin_orders_management(request):
    """Orders management section"""
    status_filter = request.GET.get("status", "all")
    search = request.GET.get("search", "")

    orders = Order.objects.select_related("user").all()

    if status_filter != "all":
        orders = orders.filter(status=status_filter)

    if search:
        orders = orders.filter(
            Q(order_id__icontains=search)
            | Q(user__username__icontains=search)
            | Q(user__email__icontains=search)
        )

    orders = orders.order_by("-created_at")

    # Order statistics
    order_stats = {
        "total": orders.count(),
        "awaiting_payment": orders.filter(status="awaiting_payment").count(),
        "paid": orders.filter(status="paid").count(),
        "shipped": orders.filter(status="shipped").count(),
        "delivered": orders.filter(status="delivered").count(),
    }

    context = {
        "orders": orders,
        "status_filter": status_filter,
        "search": search,
        "order_stats": order_stats,
    }

    return render(request, "accounts/admin/orders_management.html", context)


@login_required
@user_passes_test(is_admin)
def admin_update_order_status(request, order_id):
    """Update order status"""
    if request.method == "POST":
        order = get_object_or_404(Order, order_id=order_id)
        new_status = request.POST.get("status")

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status

            if new_status == "shipped" and not order.shipped_at:
                order.shipped_at = timezone.now()
            elif new_status == "delivered" and not order.delivered_at:
                order.delivered_at = timezone.now()

            order.save()
            messages.success(
                request,
                f"Order {order.order_id} status updated to {order.get_status_display()}.",
            )

    return redirect("accounts:admin_orders_management")


@login_required
@user_passes_test(is_admin)
def admin_refunds_management(request):
    """Refunds management section"""
    status_filter = request.GET.get("status", "all")

    refunds = Refund.objects.select_related("order__user", "invoice").all()

    if status_filter != "all":
        refunds = refunds.filter(status=status_filter)

    refunds = refunds.order_by("-created_at")

    # Refund statistics
    refund_stats = {
        "total": refunds.count(),
        "pending": refunds.filter(status="refund_pending").count(),
        "approved": refunds.filter(status="refund_approved").count(),
        "completed": refunds.filter(status="refund_completed").count(),
        "total_amount": refunds.filter(status="refund_completed").aggregate(
            total=Sum("amount")
        )["total"]
        or 0,
    }

    context = {
        "refunds": refunds,
        "status_filter": status_filter,
        "refund_stats": refund_stats,
    }

    return render(request, "accounts/admin/refunds_management.html", context)


@login_required
@user_passes_test(is_admin)
def admin_complaints_management(request):
    """Complaints management section"""
    status_filter = request.GET.get("status", "all")

    complaints = Complaint.objects.select_related("user", "order", "reason").all()

    if status_filter != "all":
        complaints = complaints.filter(status=status_filter)

    complaints = complaints.order_by("-created_at")

    # Complaint statistics
    complaint_stats = {
        "total": complaints.count(),
        "open": complaints.filter(status="open").count(),
        "in_review": complaints.filter(status="in_review").count(),
        "resolved": complaints.filter(status="resolved").count(),
    }

    context = {
        "complaints": complaints,
        "status_filter": status_filter,
        "complaint_stats": complaint_stats,
    }

    return render(request, "accounts/admin/complaints_management.html", context)


@login_required
@user_passes_test(is_admin)
def admin_payments_list(request):
    """Payments verification section"""
    status_filter = request.GET.get("status", "all")
    search = request.GET.get("search", "")

    payments = PaymentProof.objects.select_related("invoice__order__user").all()

    if status_filter == "pending":
        payments = payments.filter(verified=False, rejection_reason="")
    elif status_filter == "verified":
        payments = payments.filter(verified=True)
    elif status_filter == "rejected":
        payments = payments.exclude(rejection_reason="")

    if search:
        payments = payments.filter(
            Q(invoice__invoice_number__icontains=search)
            | Q(invoice__order__order_id__icontains=search)
            | Q(invoice__order__user__username__icontains=search)
        )

    payments = payments.order_by("-uploaded_at")

    # Payment statistics
    payment_stats = {
        "total": PaymentProof.objects.count(),
        "pending": PaymentProof.objects.filter(
            verified=False, rejection_reason=""
        ).count(),
        "verified": PaymentProof.objects.filter(verified=True).count(),
        "rejected": PaymentProof.objects.exclude(rejection_reason="").count(),
    }

    context = {
        "payments": payments,
        "status_filter": status_filter,
        "search": search,
        "payment_stats": payment_stats,
    }

    return render(request, "accounts/admin/payments_list.html", context)


@login_required
@user_passes_test(is_admin)
def admin_verify_payment(request, payment_id):
    """Verify or reject payment proof"""
    payment = get_object_or_404(PaymentProof, id=payment_id)

    if request.method == "POST":
        from payments.forms import PaymentVerificationForm

        form = PaymentVerificationForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data["action"]

            if action == "approve":
                payment.verified = True
                payment.verified_by = request.user
                payment.verified_at = timezone.now()
                payment.save()
                messages.success(
                    request,
                    f"Payment for {payment.invoice.invoice_number} has been approved.",
                )
            else:
                payment.rejection_reason = form.cleaned_data["rejection_reason"]
                payment.save()
                messages.warning(
                    request,
                    f"Payment for {payment.invoice.invoice_number} has been rejected.",
                )

            return redirect("accounts:admin_payments_list")
    else:
        from payments.forms import PaymentVerificationForm

        form = PaymentVerificationForm()

    context = {
        "payment": payment,
        "form": form,
    }

    return render(request, "accounts/admin/payment_verify.html", context)


@login_required
@user_passes_test(is_admin)
def admin_initiate_refund(request, order_id):
    """Initiate refund for an order"""
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == "POST":
        from payments.forms import RefundInitiationForm

        form = RefundInitiationForm(request.POST)

        if form.is_valid():
            from payments.services import RefundService

            refund = RefundService.initiate_refund(
                order=order,
                amount=form.cleaned_data["amount"],
                reason=form.cleaned_data["reason"],
                admin_user=request.user,
            )

            messages.success(
                request,
                f"Refund {refund.refund_number} has been initiated for order {order.order_id}.",
            )
            return redirect("accounts:admin_refunds_management")
    else:
        from payments.forms import RefundInitiationForm

        initial_data = {"amount": order.total_amount}
        form = RefundInitiationForm(initial=initial_data)

    context = {
        "order": order,
        "form": form,
    }

    return render(request, "accounts/admin/refund_initiate.html", context)


@login_required
@user_passes_test(is_admin)
def admin_upload_refund_proof(request, refund_id):
    """Upload refund proof"""
    refund = get_object_or_404(Refund, id=refund_id)

    if request.method == "POST":
        from payments.forms import RefundProofUploadForm
        from payments.models import RefundProof

        form = RefundProofUploadForm(request.POST, request.FILES)

        if form.is_valid():
            refund_proof = form.save(commit=False)
            refund_proof.refund = refund
            refund_proof.uploaded_by = request.user
            refund.refund_method = form.cleaned_data["refund_method"]
            refund.save()
            refund_proof.save()

            messages.success(
                request, f"Refund proof uploaded for {refund.refund_number}."
            )
            return redirect("accounts:admin_refunds_management")
    else:
        from payments.forms import RefundProofUploadForm

        form = RefundProofUploadForm()

    context = {
        "refund": refund,
        "form": form,
    }

    return render(request, "accounts/admin/refund_proof_upload.html", context)


@login_required
@user_passes_test(is_admin)
def admin_complaint_detail(request, complaint_id):
    """View and manage complaint details"""
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == "POST":
        from payments.forms import ComplaintStatusUpdateForm

        form = ComplaintStatusUpdateForm(request.POST)

        if form.is_valid():
            complaint.status = form.cleaned_data["status"]
            complaint.admin_notes = form.cleaned_data.get("admin_notes", "")
            complaint.resolution_notes = form.cleaned_data.get("resolution_notes", "")
            complaint.handled_by = request.user

            if complaint.status == "resolved":
                complaint.resolved_at = timezone.now()

            complaint.save()

            messages.success(
                request, f"Complaint {complaint.complaint_number} has been updated."
            )
            return redirect(
                "accounts:admin_complaint_detail", complaint_id=complaint.id
            )
    else:
        from payments.forms import ComplaintStatusUpdateForm

        initial_data = {
            "status": complaint.status,
            "admin_notes": complaint.admin_notes,
            "resolution_notes": complaint.resolution_notes,
        }
        form = ComplaintStatusUpdateForm(initial=initial_data)

    context = {
        "complaint": complaint,
        "form": form,
        "attachments": complaint.attachments.all(),
    }

    return render(request, "accounts/admin/complaint_detail.html", context)


@login_required
@user_passes_test(is_admin)
def admin_complaint_reasons(request):
    """Manage complaint reasons"""
    from payments.models import ComplaintReason

    if request.method == "POST":
        from payments.forms import ComplaintReasonForm

        form = ComplaintReasonForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Complaint reason has been added.")
            return redirect("accounts:admin_complaint_reasons")
    else:
        from payments.forms import ComplaintReasonForm

        form = ComplaintReasonForm()

    reasons = ComplaintReason.objects.all().order_by("display_order", "name")

    context = {
        "reasons": reasons,
        "form": form,
    }

    return render(request, "accounts/admin/complaint_reasons.html", context)


@login_required
@user_passes_test(is_admin)
def admin_toggle_complaint_reason(request, reason_id):
    """Toggle complaint reason active status"""
    if request.method == "POST":
        from payments.models import ComplaintReason

        reason = get_object_or_404(ComplaintReason, id=reason_id)
        reason.is_active = not reason.is_active
        reason.save()

        status = "activated" if reason.is_active else "deactivated"
        messages.success(
            request, f'Complaint reason "{reason.name}" has been {status}.'
        )

    return redirect("accounts:admin_complaint_reasons")


from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder


class DecimalEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@login_required
@staff_member_required
def admin_reports(request):
    # Get period from query params (default 30 days)
    period_days = int(request.GET.get("period", "30"))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=period_days)

    # ========== FINANCIAL ANALYTICS ==========
    orders_in_period = Order.objects.filter(created_at__gte=start_date)

    # Revenue breakdown by status
    revenue_by_status = (
        orders_in_period.values("status")
        .annotate(total=Sum("total_amount"), count=Count("id"))
        .order_by("-total")
    )

    # Payment method statistics
    payment_methods = (
        PaymentProof.objects.filter(uploaded_at__gte=start_date)
        .values("payment_method")
        .annotate(count=Count("id"), total_amount=Sum("invoice__total_amount"))
        .order_by("-count")
    )

    # Daily revenue trend
    daily_revenue = (
        orders_in_period.filter(
            status__in=["paid", "processing", "shipped", "delivered"]
        )
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(revenue=Sum("total_amount"), orders=Count("id"))
        .order_by("day")
    )

    # Financial summary
    total_revenue = (
        orders_in_period.filter(
            status__in=["paid", "processing", "shipped", "delivered"]
        ).aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    total_refunded = (
        Refund.objects.filter(
            created_at__gte=start_date, status="refund_completed"
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    net_revenue = total_revenue - total_refunded

    # Average transaction metrics
    avg_order_value = orders_in_period.aggregate(avg=Avg("total_amount"))["avg"] or 0
    avg_items_per_order = (
        OrderItem.objects.filter(order__created_at__gte=start_date)
        .values("order")
        .annotate(items=Sum("quantity"))
        .aggregate(avg=Avg("items"))["avg"]
        or 0
    )

    # ========== PRODUCT ANALYTICS ==========
    # Top products by revenue
    top_products = (
        OrderItem.objects.filter(
            order__created_at__gte=start_date,
            order__status__in=["paid", "processing", "shipped", "delivered"],
        )
        .values("product__name", "product__category__name")
        .annotate(
            total_quantity=Sum("quantity"),
            total_revenue=Sum(F("quantity") * F("price"), output_field=DecimalField()),
        )
        .order_by("-total_revenue")[:10]
    )

    # Category performance
    category_performance = (
        OrderItem.objects.filter(
            order__created_at__gte=start_date,
            order__status__in=["paid", "processing", "shipped", "delivered"],
        )
        .values("product__category__name")
        .annotate(
            total_quantity=Sum("quantity"),
            total_revenue=Sum(F("quantity") * F("price"), output_field=DecimalField()),
            unique_products=Count("product", distinct=True),
        )
        .order_by("-total_revenue")
    )

    # Specialty performance
    specialty_performance = (
        OrderItem.objects.filter(
            order__created_at__gte=start_date,
            order__status__in=["paid", "processing", "shipped", "delivered"],
            product__specialty__isnull=False,
        )
        .exclude(product__specialty="")
        .values("product__specialty")
        .annotate(
            total_revenue=Sum(F("quantity") * F("price"), output_field=DecimalField()),
            total_orders=Count("order", distinct=True),
        )
        .order_by("-total_revenue")
    )

    # Inventory insights
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=10, availability_status="in_stock"
    ).order_by("stock_quantity")[:10]

    out_of_stock_count = Product.objects.filter(
        Q(stock_quantity=0) | Q(availability_status="out_of_stock")
    ).count()

    # ========== USER ANALYTICS ==========
    # User registrations over time
    user_registrations = (
        User.objects.filter(date_joined__gte=start_date)
        .annotate(day=TruncDate("date_joined"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    # User type distribution
    from accounts.models import UserProfile

    user_types = (
        UserProfile.objects.values("user_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Active users (placed order in period)
    active_users = (
        Order.objects.filter(created_at__gte=start_date)
        .values("user")
        .distinct()
        .count()
    )

    # Customer lifetime value (top customers)
    top_customers = (
        Order.objects.filter(status__in=["paid", "processing", "shipped", "delivered"])
        .values("user__username", "user__email")
        .annotate(total_spent=Sum("total_amount"), order_count=Count("id"))
        .order_by("-total_spent")[:10]
    )

    # ========== REVIEW ANALYTICS ==========
    # Average rating by category
    ratings_by_category = (
        ProductReview.objects.filter(created_at__gte=start_date)
        .values("product__category__name")
        .annotate(avg_rating=Avg("rating"), review_count=Count("id"))
        .order_by("-avg_rating")
    )

    # Review volume trend
    review_trend = (
        ProductReview.objects.filter(created_at__gte=start_date)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"), avg_rating=Avg("rating"))
        .order_by("day")
    )

    # Rating distribution
    rating_distribution = (
        ProductReview.objects.filter(created_at__gte=start_date)
        .values("rating")
        .annotate(count=Count("id"))
        .order_by("rating")
    )

    # ========== CONTACT & SUPPORT ANALYTICS ==========
    # Contact messages by type
    contact_by_type = (
        ContactMessage.objects.filter(created_at__gte=start_date)
        .values("inquiry_type")
        .annotate(count=Count("id"), responded=Count("id", filter=Q(responded=True)))
        .order_by("-count")
    )

    # Complaint resolution rate
    total_complaints = Complaint.objects.filter(created_at__gte=start_date).count()
    resolved_complaints = Complaint.objects.filter(
        created_at__gte=start_date, status="resolved"
    ).count()
    complaint_resolution_rate = (
        (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
    )

    # Average complaint resolution time
    resolved_with_time = Complaint.objects.filter(
        created_at__gte=start_date, status="resolved", resolved_at__isnull=False
    )

    avg_resolution_time = None
    if resolved_with_time.exists():
        total_time = sum(
            [
                (c.resolved_at - c.created_at).total_seconds() / 3600
                for c in resolved_with_time
            ]
        )
        avg_resolution_time = total_time / resolved_with_time.count()

    # ========== ORDER STATISTICS ==========
    order_stats = {
        "total_orders": orders_in_period.count(),
        "total_revenue": total_revenue,
        "net_revenue": net_revenue,
        "average_order_value": avg_order_value,
        "by_status": orders_in_period.values("status").annotate(count=Count("id")),
    }

    # Payment statistics
    payment_stats = {
        "pending_verifications": PaymentProof.objects.filter(verified=False).count(),
        "verified_payments": PaymentProof.objects.filter(verified=True).count(),
        "rejected_payments": PaymentProof.objects.exclude(rejection_reason="").count(),
    }

    # Complaint statistics
    complaint_stats = {
        "open_complaints": Complaint.objects.filter(status="open").count(),
        "in_review": Complaint.objects.filter(status="in_review").count(),
        "resolved_complaints": resolved_complaints,
        "resolution_rate": complaint_resolution_rate,
        "avg_resolution_time": avg_resolution_time,
        "by_reason": Complaint.objects.filter(created_at__gte=start_date)
        .values("reason__name")
        .annotate(count=Count("id"))
        .order_by("-count"),
    }

    # Refund statistics
    refund_stats = {
        "pending_refunds": Refund.objects.filter(status="refund_pending").count(),
        "completed_refunds": Refund.objects.filter(status="refund_completed").count(),
        "total_refunded": total_refunded,
    }

    context = {
        "period": period_days,
        "start_date": start_date,
        "end_date": end_date,
        # Financial
        "order_stats": order_stats,
        "revenue_by_status": json.dumps(list(revenue_by_status), cls=DecimalEncoder),
        "payment_methods": list(payment_methods),
        "daily_revenue": json.dumps(list(daily_revenue), cls=DecimalEncoder),
        "total_revenue": total_revenue,
        "total_refunded": total_refunded,
        "net_revenue": net_revenue,
        "avg_order_value": avg_order_value,
        "avg_items_per_order": avg_items_per_order,
        # Products
        "top_products": top_products,
        "category_performance": json.dumps(
            list(category_performance), cls=DecimalEncoder
        ),
        "specialty_performance": specialty_performance,
        "low_stock_products": low_stock_products,
        "out_of_stock_count": out_of_stock_count,
        # Users
        "user_registrations": json.dumps(list(user_registrations), cls=DecimalEncoder),
        "user_types": json.dumps(list(user_types), cls=DecimalEncoder),
        "active_users": active_users,
        "top_customers": top_customers,
        "total_users": User.objects.count(),
        # Reviews
        "ratings_by_category": ratings_by_category,
        "review_trend": json.dumps(list(review_trend), cls=DecimalEncoder),
        "rating_distribution": json.dumps(
            list(rating_distribution), cls=DecimalEncoder
        ),
        # Support
        "contact_by_type": contact_by_type,
        "payment_stats": payment_stats,
        "complaint_stats": complaint_stats,
        "refund_stats": refund_stats,
    }

    return render(request, "accounts/admin/reports.html", context)
