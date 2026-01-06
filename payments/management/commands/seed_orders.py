from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from payments.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    ShippingType,
    Invoice,
    PaymentProof,
    PaymentReceipt,
    OrderNote,
    ComplaintReason,
    Complaint,
    Refund,
    RefundProof,
    Notification,
)
from products.models import Product
from decimal import Decimal
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Seeds carts, orders, and related payment data for testing"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding orders, carts, and payment data...")

        users = User.objects.all()
        products = list(Product.objects.filter(availability_status="in_stock"))

        if not users.exists() or not products:
            self.stdout.write(
                self.style.WARNING("Please run seed_users and seed_products first")
            )
            return

        # Algerian wilayas (states)
        algerian_wilayas = [
            "Algiers",
            "Oran",
            "Constantine",
            "Annaba",
            "Blida",
            "Batna",
            "Djelfa",
            "Sétif",
            "Sidi Bel Abbès",
            "Biskra",
            "Tébessa",
            "El Oued",
            "Skikda",
            "Tiaret",
            "Béjaïa",
        ]

        # Create shipping types
        self.stdout.write("Creating shipping types...")
        shipping_types = []
        shipping_data = [
            {
                "name": "Standard Shipping",
                "description": "Regular delivery service",
                "estimated_days": 7,
                "cost": Decimal("500.00"),
            },
            {
                "name": "Express Shipping",
                "description": "Fast delivery service",
                "estimated_days": 3,
                "cost": Decimal("1000.00"),
            },
            {
                "name": "Same Wilaya",
                "description": "Local delivery within same wilaya",
                "estimated_days": 2,
                "cost": Decimal("300.00"),
            },
            {
                "name": "Remote Area",
                "description": "Delivery to remote areas",
                "estimated_days": 10,
                "cost": Decimal("800.00"),
            },
        ]

        for idx, data in enumerate(shipping_data):
            shipping_type, created = ShippingType.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "estimated_days": data["estimated_days"],
                    "cost": data["cost"],
                    "is_active": True,
                    "display_order": idx,
                },
            )
            shipping_types.append(shipping_type)
            if created:
                self.stdout.write(
                    f"  ✓ Created: {shipping_type.name} - {shipping_type.cost} DZD"
                )
            else:
                self.stdout.write(f"  - Already exists: {shipping_type.name}")

        # Create complaint reasons
        self.stdout.write("Creating complaint reasons...")
        complaint_reasons_data = [
            {
                "name": "Damaged Product",
                "description": "Product arrived damaged or broken",
            },
            {"name": "Wrong Item", "description": "Received incorrect product"},
            {"name": "Missing Items", "description": "Some items missing from order"},
            {
                "name": "Late Delivery",
                "description": "Order delivered after estimated time",
            },
            {
                "name": "Quality Issues",
                "description": "Product quality below expectations",
            },
            {
                "name": "Payment Issues",
                "description": "Problems with payment processing",
            },
            {"name": "Other", "description": "Other complaints"},
        ]

        complaint_reasons = []
        for idx, data in enumerate(complaint_reasons_data):
            reason, created = ComplaintReason.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "is_active": True,
                    "display_order": idx,
                },
            )
            complaint_reasons.append(reason)
            if created:
                self.stdout.write(f"  ✓ Created: {reason.name}")
            else:
                self.stdout.write(f"  - Already exists: {reason.name}")

        # Create carts with items for each user
        for user in users:
            cart, created = Cart.objects.get_or_create(user=user)

            if created:
                num_items = random.randint(2, 5)
                cart_products = random.sample(products, min(num_items, len(products)))

                for product in cart_products:
                    CartItem.objects.get_or_create(
                        cart=cart,
                        product=product,
                        defaults={"quantity": random.randint(1, 3)},
                    )

                self.stdout.write(
                    f"Created cart for {user.username} with {num_items} items"
                )

        # Create sample orders with full workflow
        admin_users = list(User.objects.filter(is_staff=True))

        for user in users[:8]:  # Create orders for first 8 users
            for i in range(random.randint(1, 3)):
                order_products = random.sample(products, random.randint(2, 4))

                subtotal = Decimal("0.00")
                order_items_data = []

                for product in order_products:
                    quantity = random.randint(1, 3)
                    price = (
                        product.bulk_price
                        if quantity >= product.bulk_quantity and product.bulk_price
                        else product.price
                    )
                    item_total = price * quantity
                    subtotal += item_total
                    order_items_data.append(
                        {"product": product, "quantity": quantity, "price": price}
                    )

                # Tax and shipping
                tax_rate = Decimal("0.00")
                tax_amount = subtotal * tax_rate
                shipping_type = random.choice(shipping_types)
                shipping_cost = shipping_type.cost
                total_amount = subtotal + tax_amount + shipping_cost

                # Determine order status progression
                status_progression = random.choice(
                    [
                        ["pending_confirmation"],
                        ["confirmed", "awaiting_payment"],
                        ["confirmed", "awaiting_payment", "payment_under_review"],
                        ["confirmed", "awaiting_payment", "paid", "processing"],
                        [
                            "confirmed",
                            "awaiting_payment",
                            "paid",
                            "processing",
                            "shipped",
                        ],
                        [
                            "confirmed",
                            "awaiting_payment",
                            "paid",
                            "processing",
                            "shipped",
                            "delivered",
                        ],
                        ["rejected"],
                    ]
                )

                current_status = status_progression[-1]
                wilaya = random.choice(algerian_wilayas)

                order = Order.objects.create(
                    user=user,
                    status=current_status,
                    shipping_type=shipping_type,
                    shipping_address=f"{random.randint(1, 200)} Rue {random.choice(['Mohamed', 'Ahmed', 'Ali', 'Hassan'])} {random.choice(['Boudiaf', 'Khemisti', 'Amirouche', 'Larbi'])}",
                    shipping_city=wilaya,
                    shipping_state=wilaya,
                    shipping_zip=f"{random.randint(10000, 99999)}",
                    shipping_country="Algeria",
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    total_amount=total_amount,
                    created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
                )

                # Set timestamps based on status
                if current_status == "rejected":
                    order.rejected_at = order.created_at + timedelta(
                        hours=random.randint(1, 48)
                    )
                elif "confirmed" in status_progression:
                    order.confirmed_at = order.created_at + timedelta(
                        hours=random.randint(1, 24)
                    )

                if current_status in ["paid", "processing", "shipped", "delivered"]:
                    order.paid_at = order.confirmed_at + timedelta(
                        days=random.randint(1, 3)
                    )

                if current_status in ["shipped", "delivered"]:
                    order.shipped_at = order.paid_at + timedelta(
                        days=random.randint(1, 5)
                    )
                    order.tracking_number = f"DZ{random.randint(100000000, 999999999)}"

                if current_status == "delivered":
                    order.delivered_at = order.shipped_at + timedelta(
                        days=random.randint(2, 7)
                    )

                order.save()

                # Create order items
                for item_data in order_items_data:
                    OrderItem.objects.create(
                        order=order,
                        product=item_data["product"],
                        quantity=item_data["quantity"],
                        price=item_data["price"],
                    )

                # Create invoice for confirmed orders
                if "confirmed" in status_progression:
                    invoice_status = "unpaid"
                    if current_status in ["payment_under_review"]:
                        invoice_status = "payment_submitted"
                    elif current_status in [
                        "paid",
                        "processing",
                        "shipped",
                        "delivered",
                    ]:
                        invoice_status = "paid"

                    # Use get_or_create to avoid duplicate invoices
                    invoice, invoice_created = Invoice.objects.get_or_create(
                        order=order,
                        defaults={
                            "status": invoice_status,
                            "subtotal": subtotal,
                            "tax_amount": tax_amount,
                            "total_amount": total_amount,
                            "created_at": order.confirmed_at,
                        },
                    )

                    # Update status if invoice already existed
                    if not invoice_created:
                        invoice.status = invoice_status
                        if invoice_status == "paid" and not invoice.paid_at:
                            invoice.paid_at = order.paid_at
                        invoice.save()
                    elif invoice_status == "paid":
                        invoice.paid_at = order.paid_at
                        invoice.save()

                    # Create payment proof for submitted/paid invoices
                    if invoice_status in ["payment_submitted", "paid"]:
                        payment_method = random.choice(
                            ["baridimob", "ccp_cheque", "bank_transfer"]
                        )

                        # Check if payment proof already exists
                        if not PaymentProof.objects.filter(invoice=invoice).exists():
                            proof = PaymentProof.objects.create(
                                invoice=invoice,
                                payment_method=payment_method,
                                transaction_reference=f"TRX{random.randint(100000, 999999)}",
                                notes="Payment completed successfully",
                                verified=(invoice_status == "paid"),
                                uploaded_at=order.confirmed_at + timedelta(days=1),
                            )

                            if invoice_status == "paid" and admin_users:
                                proof.verified_by = random.choice(admin_users)
                                proof.verified_at = order.paid_at
                                proof.save()

                                # Create payment receipt if it doesn't exist
                                if not PaymentReceipt.objects.filter(
                                    invoice=invoice
                                ).exists():
                                    PaymentReceipt.objects.create(
                                        invoice=invoice,
                                        payment_proof=proof,
                                        amount_paid=total_amount,
                                        payment_date=order.paid_at,
                                        payment_method=payment_method,
                                    )

                # Add order notes for some orders
                if random.random() < 0.3 and admin_users:
                    note_content = random.choice(
                        [
                            "Customer requested gift wrapping",
                            "Verified address with customer",
                            "Priority delivery requested",
                            "Customer prefers delivery after 5 PM",
                            "Left package with building security",
                        ]
                    )
                    OrderNote.objects.create(
                        order=order,
                        content=note_content,
                        created_by=random.choice(admin_users),
                    )

                # Create complaints for some delivered orders
                if current_status == "delivered" and random.random() < 0.2:
                    complaint_status = random.choice(["open", "in_review", "resolved"])
                    complaint = Complaint.objects.create(
                        user=user,
                        order=order,
                        invoice=getattr(order, "invoice", None),
                        reason=random.choice(complaint_reasons),
                        description=f"Issue with order {order.order_id}. {random.choice(['Product was damaged', 'Wrong item received', 'Item missing from package'])}",
                        status=complaint_status,
                        created_at=order.delivered_at
                        + timedelta(days=random.randint(1, 5)),
                    )

                    if complaint_status in ["in_review", "resolved"] and admin_users:
                        complaint.handled_by = random.choice(admin_users)
                        complaint.admin_notes = "Investigating the issue"
                        if complaint_status == "resolved":
                            complaint.resolution_notes = (
                                "Issue resolved, replacement sent"
                            )
                            complaint.resolved_at = complaint.created_at + timedelta(
                                days=random.randint(1, 7)
                            )
                        complaint.save()

                    # Create refund for some resolved complaints
                    if complaint_status == "resolved" and random.random() < 0.5:
                        refund_amount = (
                            total_amount if random.random() < 0.5 else subtotal
                        )
                        refund = Refund.objects.create(
                            order=order,
                            invoice=order.invoice,
                            complaint=complaint,
                            amount=refund_amount,
                            reason="Compensation for complaint",
                            status="refund_completed",
                            created_at=complaint.created_at,
                            completed_at=complaint.resolved_at,
                        )

                        if admin_users:
                            refund.approved_by = random.choice(admin_users)
                            refund.processed_by = random.choice(admin_users)
                            refund.approved_at = refund.created_at + timedelta(days=1)
                            refund.processed_at = refund.approved_at + timedelta(days=1)
                            refund.save()

                # Create notifications
                Notification.objects.create(
                    user=user,
                    notification_type="order_created",
                    title="Order Created",
                    message=f"Your order {order.order_id} has been created",
                    order=order,
                    created_at=order.created_at,
                )

                if hasattr(order, "invoice"):
                    Notification.objects.create(
                        user=user,
                        notification_type="invoice_created",
                        title="Invoice Generated",
                        message=f"Invoice {order.invoice.invoice_number} is ready",
                        order=order,
                        invoice=order.invoice,
                        created_at=order.invoice.created_at,
                    )

                if current_status in ["shipped", "delivered"]:
                    Notification.objects.create(
                        user=user,
                        notification_type="order_shipped",
                        title="Order Shipped",
                        message=f"Your order {order.order_id} has been shipped. Tracking: {order.tracking_number}",
                        order=order,
                        created_at=order.shipped_at,
                    )

                self.stdout.write(
                    f"Created order {order.order_id} for {user.username} - Status: {current_status}"
                )

        self.stdout.write(
            self.style.SUCCESS("Successfully seeded all order and payment data!")
        )
