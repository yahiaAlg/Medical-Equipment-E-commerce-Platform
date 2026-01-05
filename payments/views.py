from django.shortcuts import render, redirect, get_object_or_404


from django.views.decorators.http import require_POST
import json


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from products.models import Product
from .models import *
from .forms import *
from .services import *


@login_required
def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all().select_related("product")
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
        cart_items = []

    context = {
        "cart": cart,
        "cart_items": cart_items,
    }

    return render(request, "payments/cart.html", context)


@login_required
@require_POST
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        variant_id = data.get("variant_id")
        quantity = int(data.get("quantity", 1))

        product = Product.objects.get(id=product_id)
        variant = None

        if variant_id:
            from products.models import ProductVariant

            variant = ProductVariant.objects.get(id=variant_id, product=product)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant, defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Product added to cart",
                "cart_count": cart.get_total_items(),
                "cart_total": str(cart.get_total_price()),
            }
        )

    except Product.DoesNotExist:
        return JsonResponse({"success": False, "message": "Product not found"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
@require_POST
def update_cart(request):
    try:
        data = json.loads(request.body)
        cart_item_id = data.get("cart_item_id")
        quantity = int(data.get("quantity", 1))

        cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()

        cart = cart_item.cart

        return JsonResponse(
            {
                "success": True,
                "cart_total": str(cart.get_total_price()),
                "item_total": str(cart_item.get_total_price()) if quantity > 0 else "0",
            }
        )

    except CartItem.DoesNotExist:
        return JsonResponse({"success": False, "message": "Cart item not found"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
def remove_from_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        cart_item.delete()
        messages.success(request, "Item removed from cart")
    except CartItem.DoesNotExist:
        messages.error(request, "Item not found in cart")

    return redirect("payments:cart")


# ========== USER VIEWS ==========


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("payments:cart")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        files = request.FILES.getlist("note_attachments")

        if form.is_valid():
            # Prepare shipping data
            shipping_data = {
                "shipping_type": form.cleaned_data["shipping_type"],
                "shipping_address": form.cleaned_data["shipping_address"],
                "shipping_city": form.cleaned_data["shipping_city"],
                "shipping_state": form.cleaned_data["shipping_state"],
                "shipping_zip": form.cleaned_data["shipping_zip"],
            }

            order = OrderService.create_order_from_cart(
                user=request.user, cart=cart, shipping_data=shipping_data
            )

            # Handle order note if provided
            note_content = form.cleaned_data.get("order_note")
            if note_content:
                order_note = OrderNote.objects.create(
                    order=order, content=note_content, created_by=request.user
                )

                # Handle attachments
                for file in files:
                    OrderNoteAttachment.objects.create(
                        order_note=order_note,
                        file=file,
                        file_name=file.name,
                        file_type=file.content_type,
                    )

            messages.success(
                request,
                f"Order {order.order_id} placed successfully! Awaiting admin confirmation.",
            )
            return redirect("accounts:dashboard")

    else:
        # Pre-fill with user profile data
        initial = {}
        if hasattr(request.user, "profile"):
            profile = request.user.profile
            initial = {
                "shipping_address": profile.address,
                "shipping_city": profile.city,
                "shipping_state": profile.state,
                "shipping_zip": profile.zip_code,
                "billing_same": True,
            }
        form = CheckoutForm(initial=initial)

    # Get active shipping types for display
    shipping_types = ShippingType.objects.filter(is_active=True).order_by(
        "display_order"
    )

    return render(
        request,
        "payments/checkout.html",
        {"form": form, "cart": cart, "shipping_types": shipping_types},
    )


@login_required
def invoice_list(request):
    invoices = (
        Invoice.objects.filter(order__user=request.user)
        .select_related("order")
        .order_by("-created_at")
    )
    return render(request, "payments/invoice_list.html", {"invoices": invoices})


@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, order__user=request.user)
    return render(request, "payments/invoice_detail.html", {"invoice": invoice})


@login_required
def upload_payment_proof(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, order__user=request.user)

    if invoice.status not in ["unpaid", "payment_rejected"]:
        messages.warning(
            request, "Payment proof already submitted or payment already confirmed."
        )
        return redirect("payments:invoice_detail", invoice_id=invoice.id)

    if request.method == "POST":
        form = PaymentProofUploadForm(request.POST, request.FILES)
        if form.is_valid():
            payment_proof = form.save(commit=False)
            payment_proof.invoice = invoice
            payment_proof.save()
            messages.success(
                request, "Payment proof uploaded successfully! It is now under review."
            )
            return redirect("payments:invoice_detail", invoice_id=invoice.id)
    else:
        form = PaymentProofUploadForm()

    return render(
        request,
        "payments/upload_payment_proof.html",
        {"form": form, "invoice": invoice},
    )


@login_required
def payment_receipt(request, invoice_id):
    invoice = get_object_or_404(
        Invoice, id=invoice_id, order__user=request.user, status="paid"
    )

    if not hasattr(invoice, "receipt"):
        messages.error(request, "Receipt not available.")
        return redirect("payments:invoice_detail", invoice_id=invoice.id)

    return render(
        request,
        "payments/payment_receipt.html",
        {"invoice": invoice, "receipt": invoice.receipt},
    )


@login_required
def complaint_create(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        form = ComplaintForm(request.POST)
        files = request.FILES.getlist("attachments")

        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.order = order
            complaint.invoice = order.invoice
            complaint.save()

            # Handle attachments
            for file in files:
                ComplaintAttachment.objects.create(
                    complaint=complaint, file=file, file_type=file.content_type
                )

            messages.success(
                request,
                f"Complaint {complaint.complaint_number} submitted successfully.",
            )
            return redirect("payments:complaint_detail", complaint_id=complaint.id)
    else:
        form = ComplaintForm()

    return render(
        request, "payments/complaint_create.html", {"form": form, "order": order}
    )


@login_required
def complaint_list(request):
    complaints = (
        Complaint.objects.filter(user=request.user)
        .select_related("order", "reason")
        .order_by("-created_at")
    )
    return render(request, "payments/complaint_list.html", {"complaints": complaints})


@login_required
def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)
    return render(request, "payments/complaint_detail.html", {"complaint": complaint})


@login_required
def refund_receipt(request, refund_id):
    refund = get_object_or_404(
        Refund, id=refund_id, order__user=request.user, status="refund_completed"
    )

    if not hasattr(refund, "receipt"):
        messages.error(request, "Refund receipt not available.")
        return redirect("accounts:dashboard")

    return render(
        request,
        "payments/refund_receipt.html",
        {"refund": refund, "receipt": refund.receipt},
    )


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user
    )
    notification.is_read = True
    notification.save()
    return JsonResponse({"success": True})


@login_required
def mark_all_notifications_read(request):
    NotificationService.mark_all_as_read(request.user)
    return JsonResponse({"success": True})
