from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from orders.models import Order, OrderItem
from payments.services import PaymentError, create_checkout_session
from products.models import Product


@pytest.mark.django_db
def test_create_checkout_session_for_pending_order():
    user = get_user_model().objects.create_user(
        username="stripe_checkout_buyer",
        password="test-password-only",
    )

    product = Product.objects.create(
        name="Checkout Test Product",
        description="Stripe Checkout test",
        price=Decimal("500.00"),
        stock=5,
        is_active=True,
    )

    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        total_amount=Decimal("1000.00"),
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        unit_price=Decimal("500.00"),
    )

    fake_session = SimpleNamespace(
        id="cs_test_checkout_001",
        url="https://checkout.stripe.com/test-session",
    )

    with patch("payments.services.get_stripe_client") as mock_client:
        mock_client.return_value.v1.checkout.sessions.create.return_value = (
            fake_session
        )

        session = create_checkout_session(
            order_id=order.id,
            user=user,
        )

        create_call = (
            mock_client.return_value.v1.checkout.sessions.create
        )
        create_call.assert_called_once()

        payload = create_call.call_args.args[0]

        assert payload["mode"] == "payment"
        assert payload["payment_method_types"] == ["card"]
        assert payload["client_reference_id"] == str(order.id)
        assert payload["metadata"]["order_id"] == str(order.id)
        assert payload["line_items"][0]["quantity"] == 2
        assert payload["line_items"][0]["price_data"]["unit_amount"] == 50000

    order.refresh_from_db()

    assert session.id == "cs_test_checkout_001"
    assert order.stripe_checkout_session_id == session.id

@pytest.mark.django_db
def test_existing_checkout_session_is_reused():
    user = get_user_model().objects.create_user(
        username="stripe_reuse_buyer",
    )

    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        total_amount=Decimal("500.00"),
        stripe_checkout_session_id="cs_test_existing_001",
    )

    fake_session = SimpleNamespace(
        id="cs_test_existing_001",
        url="https://checkout.stripe.com/existing-session",
        status="open",
    )

    with patch("payments.services.get_stripe_client") as mock_client:
        stripe_sessions = mock_client.return_value.v1.checkout.sessions
        stripe_sessions.retrieve.return_value = fake_session

        session = create_checkout_session(
            order_id=order.id,
            user=user,
        )

        stripe_sessions.retrieve.assert_called_once_with(
            "cs_test_existing_001"
        )
        stripe_sessions.create.assert_not_called()

    assert session.id == "cs_test_existing_001"
    assert session.url == fake_session.url

    order.refresh_from_db()
    assert order.stripe_checkout_session_id == session.id

@pytest.mark.django_db
def test_expired_checkout_session_is_rejected():
    user = get_user_model().objects.create_user(
        username="stripe_expired_buyer",
    )

    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        total_amount=Decimal("500.00"),
        stripe_checkout_session_id="cs_test_expired_001",
    )

    expired_session = SimpleNamespace(
        id="cs_test_expired_001",
        url=None,
        status="expired",
    )

    with patch("payments.services.get_stripe_client") as mock_client:
        stripe_sessions = mock_client.return_value.v1.checkout.sessions
        stripe_sessions.retrieve.return_value = expired_session

        with pytest.raises(PaymentError, match="no longer open"):
            create_checkout_session(
                order_id=order.id,
                user=user,
            )

        stripe_sessions.create.assert_not_called()

    order.refresh_from_db()

    assert order.status == Order.Status.PENDING
    assert order.stripe_checkout_session_id == "cs_test_expired_001"
