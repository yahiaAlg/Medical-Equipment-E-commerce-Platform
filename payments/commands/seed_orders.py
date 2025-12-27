from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import Cart, CartItem, Order, OrderItem
from products.models import Product
from decimal import Decimal
import random
import uuid
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Seeds carts and orders"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding orders and carts...")

        users = User.objects.all()
        products = list(Product.objects.filter(availability_status="in_stock"))

        if not users.exists() or not products:
            self.stdout.write(
                self.style.WARNING("Please run seed_users and seed_products first")
            )
            return

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
                        defaults={"quantity": random.randint(1, 5)},
                    )

                self.stdout.write(
                    f"Created cart for {user.username} with {num_items} items"
                )

        # Create sample orders
        for user in users[:3]:  # Create orders for first 3 users
            # Create 1-3 orders per user
            for i in range(random.randint(1, 3)):
                order_products = random.sample(products, random.randint(2, 4))

                subtotal = Decimal("0.00")
                order_items_data = []

                for product in order_products:
                    quantity = random.randint(1, 5)
                    price = (
                        product.bulk_price
                        if quantity >= product.bulk_quantity
                        else product.price
                    )
                    item_total = price * quantity
                    subtotal += item_total
                    order_items_data.append(
                        {"product": product, "quantity": quantity, "price": price}
                    )

                tax_amount = subtotal * Decimal("0.08")  # 8% tax
                shipping_cost = Decimal("25.00") if subtotal < 500 else Decimal("0.00")
                total_amount = subtotal + tax_amount + shipping_cost

                status = random.choice(
                    ["pending", "confirmed", "processing", "shipped", "delivered"]
                )

                order = Order.objects.create(
                    order_id=str(uuid.uuid4())[:8].upper(),
                    user=user,
                    status=status,
                    shipping_address=f"{random.randint(100, 9999)} Medical Plaza",
                    shipping_city=random.choice(
                        ["New York", "Los Angeles", "Chicago", "Houston"]
                    ),
                    shipping_state=random.choice(["NY", "CA", "IL", "TX"]),
                    shipping_zip=f"{random.randint(10000, 99999)}",
                    shipping_country="USA",
                    billing_address=f"{random.randint(100, 9999)} Medical Plaza",
                    billing_city=random.choice(
                        ["New York", "Los Angeles", "Chicago", "Houston"]
                    ),
                    billing_state=random.choice(["NY", "CA", "IL", "TX"]),
                    billing_zip=f"{random.randint(10000, 99999)}",
                    billing_country="USA",
                    payment_method=random.choice(
                        ["credit_card", "bank_transfer", "leasing"]
                    ),
                    payment_reference=f"PAY-{random.randint(100000, 999999)}",
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    total_amount=total_amount,
                    tracking_number=(
                        f"TRACK{random.randint(100000000, 999999999)}"
                        if status in ["shipped", "delivered"]
                        else ""
                    ),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
                )

                # Create order items
                for item_data in order_items_data:
                    OrderItem.objects.create(
                        order=order,
                        product=item_data["product"],
                        quantity=item_data["quantity"],
                        price=item_data["price"],
                    )

                self.stdout.write(
                    f"Created order {order.order_id} for {user.username} - ${total_amount}"
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded orders and carts!"))
