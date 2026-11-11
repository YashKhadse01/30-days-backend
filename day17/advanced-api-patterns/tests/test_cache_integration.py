
import pytest
from fastapi.testclient import TestClient

from advanced_api.main import (
    app,
    api_key_manager,
    idempotency_manager,
    items,
)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def setup_item(client):
    api_key_manager.keys.clear()
    idempotency_manager.records.clear()
    items.clear()

    # Clear only Day 17 cache keys for this test.
    # The client fixture has already started the app.
    import asyncio

    async def clear_cache():
        async for key in app.state.redis.scan_iter(
            match="day17:items:*"
        ):
            await app.state.redis.delete(key)

    # Use the TestClient event loop rather than
    # opening another asyncio loop for Redis.
    client.portal.call(clear_cache)

    key, _ = api_key_manager.create_key(
        "cache-test-client",
        {"read:items", "write:items"},
    )

    headers = {"X-API-Key": key}

    response = client.post(
        "/items",
        json={"name": "Laptop", "price": 45000},
        headers=headers,
    )

    assert response.status_code == 201

    item_id = response.json()["item"]["id"]

    yield item_id, headers

    client.portal.call(clear_cache)

    api_key_manager.keys.clear()
    idempotency_manager.records.clear()
    items.clear()

def test_first_request_cache_miss(client, setup_item):
    item_id, headers = setup_item

    response = client.get(
        f"/items/{item_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.headers["X-Cache"] == "MISS"


def test_second_request_cache_hit(client, setup_item):
    item_id, headers = setup_item

    first = client.get(
        f"/items/{item_id}",
        headers=headers,
    )

    second = client.get(
        f"/items/{item_id}",
        headers=headers,
    )

    assert first.headers["X-Cache"] == "MISS"
    assert second.headers["X-Cache"] == "HIT"


def test_update_invalidates_cache(client, setup_item):
    item_id, headers = setup_item
    url = f"/items/{item_id}"

    first = client.get(url, headers=headers)
    etag = first.headers["ETag"]

    updated = client.put(
        url,
        json={"name": "Laptop Pro", "price": 52000},
        headers={
            **headers,
            "If-Match": etag,
        },
    )

    assert updated.status_code == 200
    assert updated.headers["X-Cache"] == "INVALIDATED"

    after_update = client.get(url, headers=headers)

    assert after_update.status_code == 200
    assert after_update.headers["X-Cache"] == "MISS"
    assert after_update.json()["name"] == "Laptop Pro"


def test_cache_hit_after_update(client, setup_item):
    item_id, headers = setup_item
    url = f"/items/{item_id}"

    first = client.get(url, headers=headers)

    updated = client.put(
        url,
        json={"name": "Updated Laptop", "price": 60000},
        headers={
            **headers,
            "If-Match": first.headers["ETag"],
        },
    )

    assert updated.status_code == 200

    second = client.get(url, headers=headers)
    third = client.get(url, headers=headers)

    assert second.headers["X-Cache"] == "MISS"
    assert third.headers["X-Cache"] == "HIT"
    assert third.json()["name"] == "Updated Laptop"
