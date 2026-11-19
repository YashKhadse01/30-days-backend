
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

import pytest
from django.contrib.auth import get_user_model
from django.db import close_old_connections, connections

from cart.models import Cart, CartItem
from orders.models import Order
from orders.services import (
    InsufficientStockError,
    create_order_from_cart,
)
from products.models import Product


@pytest.mark.django_db(transaction=True)
def test_concurrent_checkout_does_not_oversell():
    User = get_user_model()

    product = Product.objects.create(
        name="Limited Stock Product",
        price=Decimal("799.00"),
        stock=1,
        is_active=True,
    )

    users = [
        User.objects.create_user(username=f"buyer_{i}")
        for i in range(2)
    ]

    for user in users:
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1,
        )

    barrier = Barrier(2)

    def checkout(user_id):
        close_old_connections()

        try:
            barrier.wait(timeout=10)

            user = User.objects.get(pk=user_id)
            create_order_from_cart(user)

            return "success"

        except InsufficientStockError:
            return "out_of_stock"

        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(checkout, [u.pk for u in users]))

    product.refresh_from_db()

    assert sorted(results) == ["out_of_stock", "success"]
    assert product.stock == 0
    assert Order.objects.filter(status=Order.Status.PENDING).count() == 1
