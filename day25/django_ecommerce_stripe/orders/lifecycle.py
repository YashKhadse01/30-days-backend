
from django.db import transaction
from django.db.models import F

from products.models import Product

from .models import Order


class OrderLifecycleError(Exception):
    """Raised for invalid order lifecycle transitions."""


@transaction.atomic
def mark_order_paid(order_id, session_id):
    """Mark an order paid after verified Stripe confirmation."""

    order = Order.objects.select_for_update().get(pk=order_id)

    if order.stripe_checkout_session_id != session_id:
        raise OrderLifecycleError("Checkout session mismatch.")

    if order.status == Order.Status.PAID:
        return order

    if order.status != Order.Status.PENDING:
        raise OrderLifecycleError(
            "Only pending orders can become paid."
        )

    order.status = Order.Status.PAID
    order.save(update_fields=["status", "updated_at"])
    return order


@transaction.atomic
def cancel_order_and_restore_stock(order_id, session_id):
    """Cancel a pending order and restore its reserved stock once."""

    order = Order.objects.select_for_update().get(pk=order_id)

    if order.stripe_checkout_session_id != session_id:
        raise OrderLifecycleError("Checkout session mismatch.")

    if order.status == Order.Status.CANCELLED:
        return order

    if order.status != Order.Status.PENDING:
        raise OrderLifecycleError(
            "Only pending orders can be cancelled."
        )

    for item in order.items.all().order_by("product_id"):
        Product.objects.filter(pk=item.product_id).update(
            stock=F("stock") + item.quantity
        )

    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    return order
