
from decimal import Decimal

from django.db import transaction

from cart.models import CartItem
from products.models import Product

from .models import Order, OrderItem


class CheckoutError(Exception):
    """Raised when an order cannot be created."""


class EmptyCartError(CheckoutError):
    """Raised when the cart contains no products."""


class InsufficientStockError(CheckoutError):
    """Raised when requested inventory is unavailable."""


@transaction.atomic
def create_order_from_cart(user):
    """
    Reserve inventory and create a pending order atomically.

    PostgreSQL row locks prevent concurrent transactions
    from reserving the same inventory twice.
    """

    # Serialize checkout attempts for the same user.
    from django.contrib.auth import get_user_model

    get_user_model().objects.select_for_update().get(pk=user.pk)

    cart_items = list(
        CartItem.objects.filter(cart__user=user)
        .select_related("product")
        .order_by("product_id")
    )

    if not cart_items:
        raise EmptyCartError("Your shopping cart is empty.")

    product_ids = [item.product_id for item in cart_items]

    # Lock products in a consistent order to reduce deadlocks.
    products = {
        product.id: product
        for product in Product.objects.select_for_update()
        .filter(id__in=product_ids)
        .order_by("id")
    }

    total = Decimal("0.00")

    for item in cart_items:
        product = products.get(item.product_id)

        if product is None or not product.is_active:
            raise CheckoutError(
                f"Product {item.product_id} is unavailable."
            )

        if product.stock < item.quantity:
            raise InsufficientStockError(
                f"Insufficient stock for {product.name}. "
                f"Available: {product.stock}, "
                f"requested: {item.quantity}."
            )

        total += product.price * item.quantity

    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        total_amount=total,
    )

    for item in cart_items:
        product = products[item.product_id]

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity,
            unit_price=product.price,
        )

        product.stock -= item.quantity
        product.save(update_fields=["stock", "updated_at"])

    CartItem.objects.filter(
        pk__in=[item.pk for item in cart_items]
    ).delete()

    return order
