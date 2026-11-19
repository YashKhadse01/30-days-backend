
import time

from django.db import transaction

from orders.models import Order

from .stripe_client import get_stripe_client


class PaymentError(Exception):
    """Raised when a Stripe Checkout Session cannot be created or reused."""


def create_checkout_session(order_id, user):
    """
    Create or reuse a Stripe Checkout Session.

    PostgreSQL row locking serializes checkout requests.
    Stripe idempotency keys protect against duplicate creation.
    """

    client = get_stripe_client()

    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .filter(pk=order_id, user=user)
            .first()
        )

        if order is None or order.status != Order.Status.PENDING:
            raise PaymentError("Pending order not found.")

        # Reuse an existing Checkout Session only if it is open.
        if order.stripe_checkout_session_id:
            try:
                session = client.v1.checkout.sessions.retrieve(
                    order.stripe_checkout_session_id
                )

            except Exception as exc:
                raise PaymentError(
                    "Unable to retrieve the existing Checkout Session."
                ) from exc

            if session.status != "open":
                raise PaymentError(
                    "Checkout Session is no longer open. "
                    "Please wait for order reconciliation "
                    "before attempting checkout again."
                )

            if not session.url:
                raise PaymentError(
                    "Checkout Session has no usable payment URL."
                )

            return session

        # Retrieve the products associated with the order.
        items = list(
            order.items.select_related("product")
        )

        if not items:
            raise PaymentError("Order contains no items.")

        # Build Stripe Checkout line items using stored order prices.
        line_items = [
            {
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": item.product.name,
                    },
                    "unit_amount": int(
                        item.unit_price * 100
                    ),
                },
                "quantity": item.quantity,
            }
            for item in items
        ]

        # Create a new Stripe Checkout Session.
        try:
            session = client.v1.checkout.sessions.create(
                {
                    "mode": "payment",
                    "payment_method_types": ["card"],
                    "line_items": line_items,
                    "success_url": (
                        "http://127.0.0.1:8001/"
                        "api/orders/?checkout=success"
                        "&session_id={CHECKOUT_SESSION_ID}"
                    ),
                    "cancel_url": (
                        "http://127.0.0.1:8001/"
                        "api/orders/?checkout=cancelled"
                    ),
                    "client_reference_id": str(order.id),
                    "metadata": {
                        "order_id": str(order.id),
                    },
                    "expires_at": int(time.time()) + 1800,
                },
                options={
                    "idempotency_key": (
                        f"day25-checkout-{order.id}"
                    ),
                },
            )

        except Exception as exc:
            raise PaymentError(
                "Unable to create Stripe Checkout Session."
            ) from exc

        # Store the Stripe Checkout Session ID.
        order.stripe_checkout_session_id = session.id

        order.save(
            update_fields=[
                "stripe_checkout_session_id",
                "updated_at",
            ]
        )

        return session
