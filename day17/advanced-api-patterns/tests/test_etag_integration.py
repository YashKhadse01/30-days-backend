
import pytest
from fastapi.testclient import TestClient
from redis import Redis

from advanced_api.main import (
    app,
    api_key_manager,
    idempotency_manager,
    items,
)


# =========================================================
# TEST CONFIGURATION
# =========================================================

# Dedicated Redis database for Day 17 tests.
# Never use this database for production data.
TEST_REDIS_URL = "redis://127.0.0.1:6380/15"


# =========================================================
# TEST FIXTURES
# =========================================================

@pytest.fixture(autouse=True)
def reset_data():
    """
    Reset API keys, idempotency records, items,
    and Redis cache between integration tests.
    """

    redis_client = Redis.from_url(
        TEST_REDIS_URL,
        decode_responses=True,
    )

    # Clear in-memory test data.
    api_key_manager.keys.clear()
    idempotency_manager.records.clear()
    items.clear()

    # Clear the dedicated test Redis database.
    redis_client.flushdb()

    yield

    # Clean up after each test.
    api_key_manager.keys.clear()
    idempotency_manager.records.clear()
    items.clear()

    redis_client.flushdb()
    redis_client.close()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    key, _ = api_key_manager.create_key(
        "etag-test-client",
        {"read:items", "write:items"},
    )

    return {"X-API-Key": key}


@pytest.fixture
def created_item(client, auth_headers):
    response = client.post(
        "/items",
        json={
            "name": "Laptop",
            "price": 45000,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    return response.json()["item"]


# =========================================================
# ETAG INTEGRATION TESTS
# =========================================================

def test_get_item_returns_etag(
    client, auth_headers, created_item
):
    response = client.get(
        f"/items/{created_item['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.headers.get("etag")
    assert response.json()["name"] == "Laptop"


def test_unchanged_item_returns_304(
    client, auth_headers, created_item
):
    url = f"/items/{created_item['id']}"

    first = client.get(
        url,
        headers=auth_headers,
    )

    etag = first.headers["etag"]

    second = client.get(
        url,
        headers={
            **auth_headers,
            "If-None-Match": etag,
        },
    )

    assert second.status_code == 304
    assert second.content == b""


def test_changed_item_returns_200(
    client, auth_headers, created_item
):
    url = f"/items/{created_item['id']}"

    first = client.get(
        url,
        headers=auth_headers,
    )

    old_etag = first.headers["etag"]

    update = client.put(
        url,
        json={
            "name": "Laptop Pro",
            "price": 50000,
        },
        headers={
            **auth_headers,
            "If-Match": old_etag,
        },
    )

    assert update.status_code == 200

    second = client.get(
        url,
        headers={
            **auth_headers,
            "If-None-Match": old_etag,
        },
    )

    assert second.status_code == 200
    assert second.headers["etag"] != old_etag


def test_update_without_if_match_returns_428(
    client, auth_headers, created_item
):
    response = client.put(
        f"/items/{created_item['id']}",
        json={
            "name": "Updated",
            "price": 50000,
        },
        headers=auth_headers,
    )

    assert response.status_code == 428


def test_stale_etag_returns_412(
    client, auth_headers, created_item
):
    response = client.put(
        f"/items/{created_item['id']}",
        json={
            "name": "Updated",
            "price": 50000,
        },
        headers={
            **auth_headers,
            "If-Match": '"stale-etag"',
        },
    )

    assert response.status_code == 412
    assert items[0]["name"] == "Laptop"


def test_correct_etag_allows_update(
    client, auth_headers, created_item
):
    url = f"/items/{created_item['id']}"

    original = client.get(
        url,
        headers=auth_headers,
    )

    etag = original.headers["etag"]

    updated = client.put(
        url,
        json={
            "name": "Laptop Pro",
            "price": 52000,
        },
        headers={
            **auth_headers,
            "If-Match": etag,
        },
    )

    assert updated.status_code == 200
    assert updated.json()["name"] == "Laptop Pro"
    assert updated.headers["etag"] != etag


def test_weak_etag_cannot_authorize_update(
    client, auth_headers, created_item
):
    url = f"/items/{created_item['id']}"

    original = client.get(
        url,
        headers=auth_headers,
    )

    etag = original.headers["etag"]

    response = client.put(
        url,
        json={
            "name": "Updated",
            "price": 50000,
        },
        headers={
            **auth_headers,
            "If-Match": f"W/{etag}",
        },
    )

    assert response.status_code == 412


def test_missing_item_returns_404(
    client, auth_headers
):
    response = client.get(
        "/items/99999",
        headers=auth_headers,
    )

    assert response.status_code == 404
