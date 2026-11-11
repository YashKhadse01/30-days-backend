
import pytest
from fastapi.testclient import TestClient

from advanced_api.main import (
    app,
    api_key_manager,
    idempotency_manager,
    items,
)


@pytest.fixture(autouse=True)
def reset_test_data():
    """Keep every integration test independent."""
    api_key_manager.keys.clear()
    idempotency_manager.records.clear()
    items.clear()

    yield

    api_key_manager.keys.clear()
    idempotency_manager.records.clear()
    items.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


# =========================================================
# 1. EXISTING API AUTHENTICATION TESTS
# =========================================================

def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_missing_api_key(client):
    response = client.get("/items")

    assert response.status_code == 401
    assert response.json()["detail"] == "API key required"


def test_invalid_api_key(client):
    response = client.get(
        "/items",
        headers={"X-API-Key": "invalid-key"},
    )

    assert response.status_code == 401


def test_valid_read_scope(client):
    key, _ = api_key_manager.create_key(
        "reporting-service",
        {"read:items"},
    )

    response = client.get(
        "/items",
        headers={"X-API-Key": key},
    )

    assert response.status_code == 200
    assert response.json()["client"] == "reporting-service"


def test_read_only_key_cannot_write(client):
    key, _ = api_key_manager.create_key(
        "reporting-service",
        {"read:items"},
    )

    response = client.post(
        "/items",
        json={
            "name": "Laptop",
            "price": 45000,
        },
        headers={"X-API-Key": key},
    )

    assert response.status_code == 403
    assert items == []


def test_valid_write_scope(client):
    key, _ = api_key_manager.create_key(
        "inventory-service",
        {"write:items"},
    )

    response = client.post(
        "/items",
        json={
            "name": "Keyboard",
            "price": 1500,
        },
        headers={"X-API-Key": key},
    )

    assert response.status_code == 201
    assert response.json()["item"]["name"] == "Keyboard"
    assert response.json()["created_by"] == "inventory-service"


def test_revoked_key_rejected(client):
    key, record = api_key_manager.create_key(
        "inventory-service",
        {"read:items"},
    )

    api_key_manager.revoke_key(record.key_id)

    response = client.get(
        "/items",
        headers={"X-API-Key": key},
    )

    assert response.status_code == 401


# =========================================================
# 2. IDEMPOTENCY INTEGRATION TESTS
# =========================================================

def test_first_idempotent_request(client):
    key, _ = api_key_manager.create_key(
        "inventory-service",
        {"write:items"},
    )

    response = client.post(
        "/items",
        json={
            "name": "Laptop",
            "price": 45000,
        },
        headers={
            "X-API-Key": key,
            "Idempotency-Key": "order-001",
        },
    )

    assert response.status_code == 201
    assert response.headers["Idempotency-Replayed"] == "false"
    assert len(items) == 1


def test_repeated_request_creates_only_one_item(client):
    key, _ = api_key_manager.create_key(
        "inventory-service",
        {"write:items"},
    )

    headers = {
        "X-API-Key": key,
        "Idempotency-Key": "order-002",
    }

    payload = {
        "name": "Keyboard",
        "price": 1500,
    }

    first = client.post(
        "/items",
        json=payload,
        headers=headers,
    )

    second = client.post(
        "/items",
        json=payload,
        headers=headers,
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()
    assert second.headers["Idempotency-Replayed"] == "true"
    assert len(items) == 1


def test_idempotency_payload_conflict(client):
    key, _ = api_key_manager.create_key(
        "inventory-service",
        {"write:items"},
    )

    headers = {
        "X-API-Key": key,
        "Idempotency-Key": "order-003",
    }

    first = client.post(
        "/items",
        json={
            "name": "Mouse",
            "price": 500,
        },
        headers=headers,
    )

    second = client.post(
        "/items",
        json={
            "name": "Mouse",
            "price": 900,
        },
        headers=headers,
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(items) == 1


def test_different_idempotency_keys_create_items(client):
    key, _ = api_key_manager.create_key(
        "inventory-service",
        {"write:items"},
    )

    for request_key in [
        "order-004",
        "order-005",
    ]:
        response = client.post(
            "/items",
            json={
                "name": "Monitor",
                "price": 12000,
            },
            headers={
                "X-API-Key": key,
                "Idempotency-Key": request_key,
            },
        )

        assert response.status_code == 201

    assert len(items) == 2


def test_idempotency_isolated_between_clients(client):
    first_key, _ = api_key_manager.create_key(
        "client-A",
        {"write:items"},
    )

    second_key, _ = api_key_manager.create_key(
        "client-B",
        {"write:items"},
    )

    for key in [first_key, second_key]:
        response = client.post(
            "/items",
            json={
                "name": "Tablet",
                "price": 20000,
            },
            headers={
                "X-API-Key": key,
                "Idempotency-Key": "shared-request-key",
            },
        )

        assert response.status_code == 201

    assert len(items) == 2


def test_blank_idempotency_key_rejected(client):
    key, _ = api_key_manager.create_key(
        "inventory-service",
        {"write:items"},
    )

    response = client.post(
        "/items",
        json={
            "name": "Printer",
            "price": 8000,
        },
        headers={
            "X-API-Key": key,
            "Idempotency-Key": " ",
        },
    )

    assert response.status_code == 400
    assert len(items) == 0
