
import pytest
import fakeredis.aioredis

from auth_hardening.rate_limiter import SlidingWindowRateLimiter


@pytest.mark.asyncio
async def test_first_five_requests_allowed():
    async with fakeredis.aioredis.FakeRedis() as redis:
        limiter = SlidingWindowRateLimiter(redis)

        results = [
            await limiter.allow("user1", limit=5, window_seconds=60)
            for _ in range(5)
        ]

        assert results == [True] * 5


@pytest.mark.asyncio
async def test_sixth_request_blocked():
    async with fakeredis.aioredis.FakeRedis() as redis:
        limiter = SlidingWindowRateLimiter(redis)

        for _ in range(5):
            assert await limiter.allow("user1", limit=5)

        assert await limiter.allow("user1", limit=5) is False


@pytest.mark.asyncio
async def test_different_users_have_separate_limits():
    async with fakeredis.aioredis.FakeRedis() as redis:
        limiter = SlidingWindowRateLimiter(redis)

        for _ in range(5):
            await limiter.allow("user1", limit=5)

        assert await limiter.allow("user1", limit=5) is False
        assert await limiter.allow("user2", limit=5) is True


@pytest.mark.asyncio
async def test_invalid_configuration_rejected():
    async with fakeredis.aioredis.FakeRedis() as redis:
        limiter = SlidingWindowRateLimiter(redis)

        with pytest.raises(ValueError):
            await limiter.allow("user1", limit=0)

        with pytest.raises(ValueError):
            await limiter.allow("user1", window_seconds=0)

@pytest.mark.asyncio
async def test_requests_allowed_after_window_expires(monkeypatch):
    current_time = [1000.0]

    monkeypatch.setattr(
        "auth_hardening.rate_limiter.time.time",
        lambda: current_time[0],
    )

    async with fakeredis.aioredis.FakeRedis() as redis:
        limiter = SlidingWindowRateLimiter(redis)

        for _ in range(5):
            assert await limiter.allow(
                "user1", limit=5, window_seconds=60
            )

        assert await limiter.allow(
            "user1", limit=5, window_seconds=60
        ) is False

        # Advance the clock beyond the 60-second window.
        current_time[0] += 61

        assert await limiter.allow(
            "user1", limit=5, window_seconds=60
        ) is True


@pytest.mark.asyncio
async def test_sliding_window_removes_only_old_requests(monkeypatch):
    current_time = [1000.0]

    monkeypatch.setattr(
        "auth_hardening.rate_limiter.time.time",
        lambda: current_time[0],
    )

    async with fakeredis.aioredis.FakeRedis() as redis:
        limiter = SlidingWindowRateLimiter(redis)

        for _ in range(3):
            assert await limiter.allow(
                "user1", limit=5, window_seconds=60
            )

        current_time[0] += 30

        for _ in range(2):
            assert await limiter.allow(
                "user1", limit=5, window_seconds=60
            )

        assert await limiter.allow(
            "user1", limit=5, window_seconds=60
        ) is False

        # First three requests expire; two recent ones remain.
        current_time[0] += 31

        for _ in range(3):
            assert await limiter.allow(
                "user1", limit=5, window_seconds=60
            )

        assert await limiter.allow(
            "user1", limit=5, window_seconds=60
        ) is False
