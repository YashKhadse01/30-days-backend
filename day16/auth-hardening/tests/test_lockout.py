
import pytest
import fakeredis.aioredis

from auth_hardening.lockout import BruteForceProtector


@pytest.mark.asyncio
async def test_account_initially_unlocked():
    async with fakeredis.aioredis.FakeRedis() as redis:
        protector = BruteForceProtector(redis)

        assert await protector.is_locked("user@example.com") is False


@pytest.mark.asyncio
async def test_first_four_failures_do_not_lock_account():
    async with fakeredis.aioredis.FakeRedis() as redis:
        protector = BruteForceProtector(redis)

        for _ in range(4):
            locked = await protector.record_failure(
                "user@example.com"
            )
            assert locked is False

        assert await protector.is_locked("user@example.com") is False


@pytest.mark.asyncio
async def test_fifth_failure_locks_account():
    async with fakeredis.aioredis.FakeRedis() as redis:
        protector = BruteForceProtector(redis)

        for _ in range(5):
            locked = await protector.record_failure(
                "user@example.com"
            )

        assert locked is True
        assert await protector.is_locked("user@example.com") is True


@pytest.mark.asyncio
async def test_accounts_have_independent_lockouts():
    async with fakeredis.aioredis.FakeRedis() as redis:
        protector = BruteForceProtector(redis)

        for _ in range(5):
            await protector.record_failure("user1@example.com")

        assert await protector.is_locked("user1@example.com") is True
        assert await protector.is_locked("user2@example.com") is False


@pytest.mark.asyncio
async def test_success_resets_failure_counter():
    async with fakeredis.aioredis.FakeRedis() as redis:
        protector = BruteForceProtector(redis)

        for _ in range(4):
            await protector.record_failure("user@example.com")

        await protector.record_success("user@example.com")

        assert (
            await protector.record_failure("user@example.com")
            is False
        )


@pytest.mark.asyncio
async def test_success_does_not_clear_active_lock():
    async with fakeredis.aioredis.FakeRedis() as redis:
        protector = BruteForceProtector(redis)

        for _ in range(5):
            await protector.record_failure("user@example.com")

        await protector.record_success("user@example.com")

        assert await protector.is_locked("user@example.com") is True


@pytest.mark.asyncio
async def test_case_insensitive_account_identifiers():
    async with fakeredis.aioredis.FakeRedis() as redis:
        protector = BruteForceProtector(redis)

        for _ in range(5):
            await protector.record_failure("USER@EXAMPLE.COM")

        assert await protector.is_locked("user@example.com") is True


@pytest.mark.asyncio
async def test_invalid_settings_rejected():
    async with fakeredis.aioredis.FakeRedis() as redis:
        protector = BruteForceProtector(redis)

        with pytest.raises(ValueError):
            await protector.record_failure(
                "user@example.com",
                max_attempts=0,
            )

        with pytest.raises(ValueError):
            await protector.record_failure(
                "user@example.com",
                lock_seconds=0,
            )

        with pytest.raises(ValueError):
            await protector.is_locked("")

@pytest.mark.asyncio
async def test_account_unlocks_after_lock_expiry():
    async with fakeredis.aioredis.FakeRedis() as redis:
        protector = BruteForceProtector(redis)
        account = "user@example.com"

        for _ in range(5):
            await protector.record_failure(
                account,
                lock_seconds=300,
            )

        assert await protector.is_locked(account) is True

        # Simulate expiration of the Redis lock key.
        _, lock_key = protector._keys(account)
        await redis.delete(lock_key)

        assert await protector.is_locked(account) is False

        # A new failure starts a fresh counter.
        assert await protector.record_failure(account) is False


@pytest.mark.asyncio
async def test_locked_account_remains_locked_on_more_failures():
    async with fakeredis.aioredis.FakeRedis() as redis:
        protector = BruteForceProtector(redis)
        account = "user@example.com"

        for _ in range(5):
            await protector.record_failure(account)

        assert await protector.is_locked(account) is True

        # Further failures must not remove the lock.
        assert await protector.record_failure(account) is True
        assert await protector.is_locked(account) is True
