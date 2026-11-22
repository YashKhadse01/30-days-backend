"""Tests for Redis caching and rate limiting."""

import json
from unittest.mock import AsyncMock

import pytest

from capstone_core.services.cache import RedisCache
from capstone_core.services.rate_limit import RedisRateLimiter


@pytest.mark.asyncio
async def test_cache_set_with_ttl() -> None:
    redis = AsyncMock()
    cache = RedisCache(redis)

    await cache.set("item-1", {"status": "ready"}, ttl_seconds=120)

    redis.set.assert_awaited_once_with(
        "cache:item-1",
        json.dumps({"status": "ready"}),
        ex=120,
    )


@pytest.mark.asyncio
async def test_cache_get_and_delete() -> None:
    redis = AsyncMock()
    redis.get.return_value = '{"value":42}'
    cache = RedisCache(redis)

    assert await cache.get("item-1") == {"value": 42}

    await cache.delete("item-1")
    redis.delete.assert_awaited_once_with("cache:item-1")


@pytest.mark.asyncio
async def test_cache_miss() -> None:
    redis = AsyncMock()
    redis.get.return_value = None

    assert await RedisCache(redis).get("missing") is None


@pytest.mark.asyncio
async def test_cache_rejects_invalid_ttl() -> None:
    with pytest.raises(ValueError):
        await RedisCache(AsyncMock()).set("key", {}, ttl_seconds=0)


@pytest.mark.asyncio
async def test_rate_limit_allows_requests(monkeypatch) -> None:
    monkeypatch.setattr(
        "capstone_core.services.rate_limit.time.time",
        lambda: 120.0,
    )

    redis = AsyncMock()
    redis.eval.side_effect = [1, 2, 3]

    limiter = RedisRateLimiter(redis)

    assert await limiter.allow("user-1", limit=2)
    assert await limiter.allow("user-1", limit=2)
    assert not await limiter.allow("user-1", limit=2)

    assert redis.eval.await_count == 3
    for call in redis.eval.await_args_list:
        assert call.args[1:] == (1, "rate:user-1:2", 120)

    redis.expire.assert_not_awaited()


@pytest.mark.asyncio
async def test_rate_limit_rejects_invalid_configuration() -> None:
    limiter = RedisRateLimiter(AsyncMock())

    with pytest.raises(ValueError):
        await limiter.allow("user-1", limit=0)
