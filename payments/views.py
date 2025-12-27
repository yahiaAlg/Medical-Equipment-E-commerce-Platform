from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
import json
import uuid
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm
from products.models import Product


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
        quantity = int(data.get("quantity", 1))

        product = Product.objects.get(id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
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


@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all().select_related("product")

        if not cart_items:
            messages.warning(request, "Your cart is empty")
            return redirect("payments:cart")

    except Cart.DoesNotExist:
        messages.warning(request, "Your cart is empty")
        return redirect("payments:cart")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Store checkout data in session
            request.session["checkout_data"] = form.cleaned_data
            return redirect("payments:checkout_confirm")
    else:
        # Pre-fill form with user profile data
        initial_data = {}
        if hasattr(request.user, "profile"):
            profile = request.user.profile
            initial_data = {
                "shipping_address": profile.address,
                "shipping_city": profile.city,
                "shipping_state": profile.state,
                "shipping_zip": profile.zip_code,
                "shipping_country": profile.country,
                "billing_address": profile.address,
                "billing_city": profile.city,
                "billing_state": profile.state,
                "billing_zip": profile.zip_code,
                "billing_country": profile.country,
            }

        form = CheckoutForm(initial=initial_data)

    context = {
        "form": form,
        "cart": cart,
        "cart_items": cart_items,
    }

    return render(request, "payments/checkout.html", context)


@login_required
def checkout_confirm(request):
    checkout_data = request.session.get("checkout_data")
    if not checkout_data:
        messages.error(request, "Checkout session expired")
        return redirect("payments:checkout")

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all().select_related("product")

        if not cart_items:
            messages.warning(request, "Your cart is empty")
            return redirect("payments:cart")

    except Cart.DoesNotExist:
        messages.warning(request, "Your cart is empty")
        return redirect("payments:cart")

    if request.method == "POST":
        # Process the order
        with transaction.atomic():
            # Calculate totals
            subtotal = cart.get_total_price()
            tax_amount = subtotal * Decimal("0.08")  # 8% tax
            shipping_cost = (
                Decimal("25.00") if subtotal < 500 else Decimal("0")
            )  # Free shipping over $500
            total_amount = subtotal + tax_amount + shipping_cost

            # Create order
            order = Order.objects.create(
                order_id=str(uuid.uuid4()),
                user=request.user,
                shipping_address=checkout_data["shipping_address"],
                shipping_city=checkout_data["shipping_city"],
                shipping_state=checkout_data["shipping_state"],
                shipping_zip=checkout_data["shipping_zip"],
                shipping_country=checkout_data["shipping_country"],
                billing_address=checkout_data["billing_address"],
                billing_city=checkout_data["billing_city"],
                billing_state=checkout_data["billing_state"],
                billing_zip=checkout_data["billing_zip"],
                billing_country=checkout_data["billing_country"],
                payment_method=checkout_data["payment_method"],
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_cost=shipping_cost,
                total_amount=total_amount,
                status="confirmed",
            )

            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=(
                        cart_item.product.bulk_price
                        if cart_item.quantity >= cart_item.product.bulk_quantity
                        and cart_item.product.bulk_price
                        else cart_item.product.price
                    ),
                )

                # Update product stock
                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()

            # Clear cart
            cart_items.delete()

            # Clear session
            del request.session["checkout_data"]

            # Send confirmation email
            try:
                send_mail(
                    subject=f"Order Confirmation - {order.order_id}",
                    message=f"Thank you for your order! Your order #{order.order_id} has been confirmed.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, "Your order has been placed successfully!")
            return redirect("payments:order_success", order_id=order.order_id)

    # Calculate totals
    subtotal = cart.get_total_price()
    tax_amount = subtotal * Decimal("0.08")  # 8% tax
    shipping_cost = (
        Decimal("25.00") if subtotal < 500 else Decimal("0")
    )  # Free shipping over $500
    total_amount = subtotal + tax_amount + shipping_cost
    delivery_start = datetime.now() + timedelta(days=5)
    delivery_end = datetime.now() + timedelta(days=7)

    context = {
        "checkout_data": checkout_data,
        "cart": cart,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "shipping_cost": shipping_cost,
        "total_amount": total_amount,
        "delivery_start": delivery_start,
        "delivery_end": delivery_end,
    }

    return render(request, "payments/checkout_confirm.html", context)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    # Calculate delivery dates
    delivery_start = order.created_at + timedelta(days=5)
    delivery_end = order.created_at + timedelta(days=7)

    context = {
        "order": order,
        "delivery_start": delivery_start,
        "delivery_end": delivery_end,
    }

    return render(request, "payments/order_success.html", context)


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    context = {
        "orders": orders,
    }

    return render(request, "payments/order_list.html", context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    # Calculate estimated delivery
    delivery_estimate = order.created_at + timedelta(days=5)

    context = {
        "order": order,
        "delivery_estimate": delivery_estimate,
    }

    return render(request, "payments/order_detail.html", context)
