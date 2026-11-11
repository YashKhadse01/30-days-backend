
import asyncio

import fakeredis.aioredis
import pytest

from advanced_api.cache import CacheAsideManager


@pytest.fixture
def redis_client():
    return fakeredis.aioredis.FakeRedis(
        decode_responses=True
    )


@pytest.fixture
def cache(redis_client):
    return CacheAsideManager(
        redis=redis_client,
        ttl_seconds=60,
    )


@pytest.mark.asyncio
async def test_cache_miss_loads_data(cache):
    calls = 0

    async def loader():
        nonlocal calls
        calls += 1
        return {"id": 1, "name": "Laptop"}

    data, hit = await cache.get_or_load(
        "item:1",
        loader,
    )

    assert data == {"id": 1, "name": "Laptop"}
    assert hit is False
    assert calls == 1


@pytest.mark.asyncio
async def test_cache_hit_avoids_loader(cache):
    calls = 0

    async def loader():
        nonlocal calls
        calls += 1
        return {"id": 1, "name": "Laptop"}

    await cache.get_or_load("item:1", loader)

    data, hit = await cache.get_or_load(
        "item:1",
        loader,
    )

    assert hit is True
    assert data["name"] == "Laptop"
    assert calls == 1


@pytest.mark.asyncio
async def test_cache_invalidation(cache):
    async def loader():
        return {"id": 1}

    await cache.get_or_load("item:1", loader)

    deleted = await cache.invalidate("item:1")

    assert deleted is True

    _, hit = await cache.get_or_load(
        "item:1",
        loader,
    )

    assert hit is False


@pytest.mark.asyncio
async def test_invalidate_missing_key(cache):
    result = await cache.invalidate("missing")

    assert result is False


@pytest.mark.asyncio
async def test_set_value(cache):
    await cache.set_value(
        "item:2",
        {"id": 2, "name": "Mouse"},
    )

    async def loader():
        raise AssertionError(
            "Loader should not execute"
        )

    data, hit = await cache.get_or_load(
        "item:2",
        loader,
    )

    assert hit is True
    assert data["name"] == "Mouse"


@pytest.mark.asyncio
async def test_cache_expiration(redis_client):
    cache = CacheAsideManager(
        redis_client,
        ttl_seconds=1,
    )

    calls = 0

    async def loader():
        nonlocal calls
        calls += 1
        return {"count": calls}

    await cache.get_or_load("expiring", loader)

    await asyncio.sleep(1.1)

    data, hit = await cache.get_or_load(
        "expiring",
        loader,
    )

    assert hit is False
    assert data["count"] == 2


@pytest.mark.asyncio
async def test_none_result_not_cached(cache):
    calls = 0

    async def loader():
        nonlocal calls
        calls += 1
        return None

    first, first_hit = await cache.get_or_load(
        "missing-item",
        loader,
    )

    second, second_hit = await cache.get_or_load(
        "missing-item",
        loader,
    )

    assert first is None
    assert second is None
    assert first_hit is False
    assert second_hit is False
    assert calls == 2


@pytest.mark.asyncio
async def test_empty_cache_key_rejected(cache):
    async def loader():
        return {"ok": True}

    with pytest.raises(ValueError):
        await cache.get_or_load("", loader)


@pytest.mark.asyncio
async def test_empty_invalidation_key_rejected(cache):
    with pytest.raises(ValueError):
        await cache.invalidate("")


@pytest.mark.asyncio
async def test_empty_set_key_rejected(cache):
    with pytest.raises(ValueError):
        await cache.set_value("", {"ok": True})


def test_invalid_ttl_rejected(redis_client):
    with pytest.raises(ValueError):
        CacheAsideManager(
            redis_client,
            ttl_seconds=0,
        )


@pytest.mark.asyncio
async def test_cache_preserves_nested_data(cache):
    original = {
        "id": 3,
        "details": {
            "category": "electronics",
            "tags": ["office", "hardware"],
        },
    }

    async def loader():
        return original

    await cache.get_or_load("item:3", loader)

    cached, hit = await cache.get_or_load(
        "item:3",
        loader,
    )

    assert hit is True
    assert cached == original
