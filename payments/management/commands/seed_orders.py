from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from payments.models import Cart, CartItem, Order, OrderItem
from products.models import Product
from decimal import Decimal
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Seeds carts and orders for testing"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding orders and carts...")

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

        # Create carts with items for each user
        for user in users:
            cart, created = Cart.objects.get_or_create(user=user)

            if created:
                # Add 2-5 random products to cart
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

        # Create sample orders
        for user in users[:5]:  # Create orders for first 5 users
            # Create 1-3 orders per user
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

                # Calculate based on Algeria tax and shipping
                tax_rate = Decimal("0.19")  # 19% tax for Algeria
                tax_amount = subtotal * tax_rate
                shipping_cost = Decimal("500.00")  # Fixed shipping for Algeria
                total_amount = subtotal + tax_amount + shipping_cost

                # Random status from available choices
                status = random.choice(
                    [
                        "awaiting_payment",
                        "payment_under_review",
                        "paid",
                        "processing",
                        "shipped",
                        "delivered",
                    ]
                )

                # Random wilaya (state)
                wilaya = random.choice(algerian_wilayas)

                order = Order.objects.create(
                    user=user,
                    status=status,
                    shipping_address=f"{random.randint(1, 200)} Rue {random.choice(['Mohamed', 'Ahmed', 'Ali', 'Hassan'])} {random.choice(['Boudiaf', 'Khemisti', 'Amirouche', 'Larbi'])}",
                    shipping_city=wilaya,
                    shipping_state=wilaya,
                    shipping_zip=f"{random.randint(10000, 99999)}",
                    shipping_country="Algeria",
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    total_amount=total_amount,
                    tracking_number=(
                        f"DZ{random.randint(100000000, 999999999)}"
                        if status in ["shipped", "delivered"]
                        else ""
                    ),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
                )

                # Set paid_at for paid orders
                if status in ["paid", "processing", "shipped", "delivered"]:
                    from django.utils import timezone

                    order.paid_at = order.created_at + timedelta(
                        days=random.randint(1, 3)
                    )
                    order.save()

                # Set shipped_at for shipped orders
                if status in ["shipped", "delivered"]:
                    order.shipped_at = order.paid_at + timedelta(
                        days=random.randint(1, 5)
                    )
                    order.save()

                # Set delivered_at for delivered orders
                if status == "delivered":
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

                    # Reduce stock
                    product = item_data["product"]
                    product.stock_quantity -= item_data["quantity"]
                    product.save()

                self.stdout.write(
                    f"Created order {order.order_id} for {user.username} - {total_amount} DZD"
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded orders and carts!"))
