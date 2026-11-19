
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from cart.models import Cart, CartItem
from products.models import Product


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="cart_test_user",
        password="test-password-123",
    )


@pytest.fixture
def client(user):
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def product(db):
    return Product.objects.create(
        name="Test Wireless Mouse",
        description="Test product",
        price=Decimal("799.00"),
        stock=10,
        is_active=True,
    )


@pytest.mark.django_db
def test_empty_cart(client):
    response = client.get("/api/cart/")

    assert response.status_code == 200
    assert response.data["items"] == []
    assert Decimal(response.data["total"]) == Decimal("0.00")


@pytest.mark.django_db
def test_add_product_to_cart(client, user, product):
    response = client.post(
        "/api/cart/items/",
        {"product_id": product.id, "quantity": 2},
        format="json",
    )

    assert response.status_code == 201
    assert CartItem.objects.get(cart__user=user).quantity == 2


@pytest.mark.django_db
def test_add_same_product_updates_quantity(client, user, product):
    payload = {"product_id": product.id, "quantity": 2}

    first = client.post("/api/cart/items/", payload, format="json")
    second = client.post("/api/cart/items/", payload, format="json")

    assert first.status_code == 201
    assert second.status_code == 200
    assert CartItem.objects.get(cart__user=user).quantity == 4
    assert CartItem.objects.filter(cart__user=user).count() == 1


@pytest.mark.django_db
def test_cart_total(client, product):
    client.post(
        "/api/cart/items/",
        {"product_id": product.id, "quantity": 2},
        format="json",
    )

    response = client.get("/api/cart/")

    assert response.status_code == 200
    assert Decimal(response.data["total"]) == Decimal("1598.00")


@pytest.mark.django_db
def test_update_cart_quantity(client, user, product):
    cart = Cart.objects.create(user=user)
    item = CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=1,
    )

    response = client.patch(
        f"/api/cart/items/{item.id}/",
        {"quantity": 5},
        format="json",
    )

    assert response.status_code == 200
    item.refresh_from_db()
    assert item.quantity == 5


@pytest.mark.django_db
def test_remove_cart_item(client, user, product):
    cart = Cart.objects.create(user=user)
    item = CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=1,
    )

    response = client.delete(f"/api/cart/items/{item.id}/")

    assert response.status_code == 204
    assert not CartItem.objects.filter(pk=item.pk).exists()


@pytest.mark.django_db
def test_cart_requires_authentication(db):
    anonymous_client = APIClient()

    response = anonymous_client.get("/api/cart/")

    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_cannot_access_another_users_cart_item(client, product):
    other_user = get_user_model().objects.create_user(
        username="another_user",
        password="test-password-456",
    )
    other_cart = Cart.objects.create(user=other_user)
    item = CartItem.objects.create(
        cart=other_cart,
        product=product,
        quantity=1,
    )

    response = client.patch(
        f"/api/cart/items/{item.id}/",
        {"quantity": 5},
        format="json",
    )

    assert response.status_code == 404
    item.refresh_from_db()
    assert item.quantity == 1
