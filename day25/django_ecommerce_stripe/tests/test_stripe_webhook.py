
import hashlib
import hmac
import json
import time
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from products.models import Product

WEBHOOK_URL = "/api/payments/webhook/"
TEST_WEBHOOK_SECRET = "whsec_local_test_only"


def make_signature(payload, secret, timestamp=None):
    """Create a Stripe-compatible test signature."""
    if timestamp is None:
        timestamp = int(time.time())

    signed_payload = f"{timestamp}.".encode() + payload

    signature = hmac.new(
        secret.encode(),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    return f"t={timestamp},v1={signature}"


def make_event(event_type="checkout.session.completed"):
    return {
        "id": "evt_test_webhook_001",
        "object": "event",
        "type": event_type,
        "data": {
            "object": {
                "id": "cs_test_example",
                "object": "checkout.session",
                "payment_status": "unpaid",
                "metadata": {"order_id": "1"},
            }
        },
    }


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET="")
def test_webhook_requires_configuration():
    client = APIClient()

    response = client.post(
        WEBHOOK_URL,
        data=b"{}",
        content_type="application/json",
    )

    assert response.status_code == 503


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_webhook_rejects_missing_signature():
    client = APIClient()

    response = client.post(
        WEBHOOK_URL,
        data=b"{}",
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_webhook_rejects_invalid_signature():
    client = APIClient()
    payload = json.dumps(make_event()).encode()

    response = client.post(
        WEBHOOK_URL,
        data=payload,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="t=123,v1=invalid",
    )

    assert response.status_code == 400


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_webhook_accepts_valid_signature_for_ignored_event():
    client = APIClient()

    payload = json.dumps(
        make_event("customer.created")
    ).encode()

    response = client.post(
        WEBHOOK_URL,
        data=payload,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=make_signature(
            payload,
            TEST_WEBHOOK_SECRET,
        ),
    )

    assert response.status_code == 200


@pytest.fixture
def webhook_order(db):
    user = get_user_model().objects.create_user(
        username="webhook_payment_buyer"
    )

    product = Product.objects.create(
        name="Webhook Test Product",
        description="Payment verification test",
        price=Decimal("500.00"),
        stock=3,
        is_active=True,
    )

    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        total_amount=Decimal("1000.00"),
        stripe_checkout_session_id="cs_test_webhook_order",
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        unit_price=Decimal("500.00"),
    )

    return order, product


def send_signed_event(client, event):
    payload = json.dumps(event).encode()

    return client.post(
        WEBHOOK_URL,
        data=payload,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=make_signature(
            payload,
            TEST_WEBHOOK_SECRET,
        ),
    )


def payment_event(order, event_type, payment_status="paid"):
    return {
        "id": f"evt_test_{event_type.replace('.', '_')}",
        "object": "event",
        "type": event_type,
        "data": {
            "object": {
                "id": order.stripe_checkout_session_id,
                "object": "checkout.session",
                "client_reference_id": str(order.id),
                "payment_status": payment_status,
                "currency": "inr",
                "amount_total": 100000,
                "metadata": {"order_id": str(order.id)},
            }
        },
    }


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_signed_payment_marks_order_paid(webhook_order):
    order, _ = webhook_order
    client = APIClient()

    event = payment_event(
        order,
        "checkout.session.completed",
    )
    response = send_signed_event(client, event)
    print("Webhook status:", response.status_code)
    print("Webhook response:", response.content.decode())

    order.refresh_from_db()

    assert response.status_code == 200
    assert order.status == Order.Status.PAID


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_duplicate_payment_webhook_is_idempotent(webhook_order):
    order, _ = webhook_order
    client = APIClient()

    event = payment_event(
        order,
        "checkout.session.completed",
    )

    first = send_signed_event(client, event)
    second = send_signed_event(client, event)

    order.refresh_from_db()

    assert first.status_code == 200
    assert second.status_code == 200
    assert order.status == Order.Status.PAID


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_wrong_payment_amount_is_rejected(webhook_order):
    order, _ = webhook_order
    client = APIClient()

    event = payment_event(
        order,
        "checkout.session.completed",
    )
    event["data"]["object"]["amount_total"] = 100

    response = send_signed_event(client, event)

    order.refresh_from_db()

    assert response.status_code == 400
    assert order.status == Order.Status.PENDING


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_wrong_currency_is_rejected(webhook_order):
    order, _ = webhook_order
    client = APIClient()

    event = payment_event(
        order,
        "checkout.session.completed",
    )
    event["data"]["object"]["currency"] = "usd"

    response = send_signed_event(client, event)

    order.refresh_from_db()

    assert response.status_code == 400
    assert order.status == Order.Status.PENDING


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_duplicate_expiration_restores_stock_once(webhook_order):
    order, product = webhook_order
    client = APIClient()

    event = payment_event(
        order,
        "checkout.session.expired",
        payment_status="unpaid",
    )

    first = send_signed_event(client, event)
    second = send_signed_event(client, event)

    order.refresh_from_db()
    product.refresh_from_db()

    assert first.status_code == 200
    assert second.status_code == 200
    assert order.status == Order.Status.CANCELLED
    assert product.stock == 5


@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_expiration_after_payment_does_not_restore_stock(webhook_order):
    order, product = webhook_order
    client = APIClient()

    paid_event = payment_event(
        order,
        "checkout.session.completed",
    )
    expired_event = payment_event(
        order,
        "checkout.session.expired",
        payment_status="unpaid",
    )

    paid_response = send_signed_event(
        client,
        paid_event,
    )
    expired_response = send_signed_event(
        client,
        expired_event,
    )

    order.refresh_from_db()
    product.refresh_from_db()

    assert paid_response.status_code == 200
    assert expired_response.status_code == 409
    assert order.status == Order.Status.PAID
    assert product.stock == 3

@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_async_payment_failure_preserves_pending_order(webhook_order):
    order, product = webhook_order
    client = APIClient()

    event = payment_event(
        order,
        "checkout.session.async_payment_failed",
        payment_status="unpaid",
    )

    response = send_signed_event(client, event)

    order.refresh_from_db()
    product.refresh_from_db()

    assert response.status_code == 200
    assert order.status == Order.Status.PENDING
    assert product.stock == 3

@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_expiration_rejects_mismatched_checkout_session(webhook_order):
    order, product = webhook_order
    client = APIClient()

    event = payment_event(
        order,
        "checkout.session.expired",
        payment_status="unpaid",
    )

    # Simulate a signed event referencing a different session.
    event["data"]["object"]["id"] = "cs_test_different_session"

    response = send_signed_event(client, event)

    order.refresh_from_db()
    product.refresh_from_db()

    assert response.status_code == 409
    assert order.status == Order.Status.PENDING
    assert product.stock == 3

@pytest.mark.django_db
@override_settings(STRIPE_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
def test_async_failure_rejects_mismatched_session(webhook_order):
    order, product = webhook_order
    client = APIClient()

    event = payment_event(
        order,
        "checkout.session.async_payment_failed",
        payment_status="unpaid",
    )

    event["data"]["object"]["id"] = "cs_wrong_session"

    response = send_signed_event(client, event)

    order.refresh_from_db()
    product.refresh_from_db()

    assert response.status_code == 409
    assert order.status == Order.Status.PENDING
    assert product.stock == 3
