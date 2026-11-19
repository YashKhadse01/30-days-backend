
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from orders.lifecycle import (
    OrderLifecycleError,
    cancel_order_and_restore_stock,
    mark_order_paid,
)
from orders.models import Order, OrderItem
from products.models import Product


@pytest.fixture
def pending_order(db):
    user = get_user_model().objects.create_user(
        username="lifecycle_buyer",
        password="test-password-123",
    )

    product = Product.objects.create(
        name="Lifecycle Test Product",
        description="Test inventory restoration",
        price=Decimal("500.00"),
        stock=3,
        is_active=True,
    )

    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        total_amount=Decimal("1000.00"),
        stripe_checkout_session_id="cs_test_lifecycle_123",
    )

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        unit_price=Decimal("500.00"),
    )

    return order, product


@pytest.mark.django_db
def test_payment_confirmation(pending_order):
    order, _ = pending_order

    mark_order_paid(order.id, "cs_test_lifecycle_123")

    order.refresh_from_db()
    assert order.status == Order.Status.PAID


@pytest.mark.django_db
def test_duplicate_payment_confirmation(pending_order):
    order, _ = pending_order

    mark_order_paid(order.id, "cs_test_lifecycle_123")
    mark_order_paid(order.id, "cs_test_lifecycle_123")

    order.refresh_from_db()
    assert order.status == Order.Status.PAID


@pytest.mark.django_db
def test_expiration_restores_stock(pending_order):
    order, product = pending_order

    cancel_order_and_restore_stock(
        order.id,
        "cs_test_lifecycle_123",
    )

    order.refresh_from_db()
    product.refresh_from_db()

    assert order.status == Order.Status.CANCELLED
    assert product.stock == 5


@pytest.mark.django_db
def test_duplicate_expiration_does_not_restore_twice(pending_order):
    order, product = pending_order

    cancel_order_and_restore_stock(
        order.id,
        "cs_test_lifecycle_123",
    )
    cancel_order_and_restore_stock(
        order.id,
        "cs_test_lifecycle_123",
    )

    product.refresh_from_db()
    assert product.stock == 5


@pytest.mark.django_db
def test_expiration_after_payment_is_rejected(pending_order):
    order, product = pending_order

    mark_order_paid(order.id, "cs_test_lifecycle_123")

    with pytest.raises(OrderLifecycleError):
        cancel_order_and_restore_stock(
            order.id,
            "cs_test_lifecycle_123",
        )

    product.refresh_from_db()
    assert product.stock == 3


@pytest.mark.django_db
def test_payment_after_expiration_is_rejected(pending_order):
    order, product = pending_order

    cancel_order_and_restore_stock(
        order.id,
        "cs_test_lifecycle_123",
    )

    with pytest.raises(OrderLifecycleError):
        mark_order_paid(order.id, "cs_test_lifecycle_123")

    product.refresh_from_db()
    assert product.stock == 5


@pytest.mark.django_db
def test_wrong_session_cannot_confirm_payment(pending_order):
    order, _ = pending_order

    with pytest.raises(OrderLifecycleError):
        mark_order_paid(order.id, "cs_test_wrong_session")

    order.refresh_from_db()
    assert order.status == Order.Status.PENDING


@pytest.mark.django_db
def test_wrong_session_cannot_restore_inventory(pending_order):
    order, product = pending_order

    with pytest.raises(OrderLifecycleError):
        cancel_order_and_restore_stock(
            order.id,
            "cs_test_wrong_session",
        )

    product.refresh_from_db()
    assert product.stock == 3
