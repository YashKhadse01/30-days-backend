
import hashlib

import fakeredis.aioredis
import pytest

from auth_hardening.password_reset import PasswordResetManager


@pytest.mark.asyncio
async def test_create_and_consume_token():
    async with fakeredis.aioredis.FakeRedis() as redis:
        manager = PasswordResetManager(redis)

        token = await manager.create_token("user-123")

        assert isinstance(token, str)
        assert len(token) >= 40
        assert await manager.consume_token(token) == "user-123"


@pytest.mark.asyncio
async def test_token_is_single_use():
    async with fakeredis.aioredis.FakeRedis() as redis:
        manager = PasswordResetManager(redis)

        token = await manager.create_token("user-123")

        assert await manager.consume_token(token) == "user-123"
        assert await manager.consume_token(token) is None


@pytest.mark.asyncio
async def test_invalid_token_rejected():
    async with fakeredis.aioredis.FakeRedis() as redis:
        manager = PasswordResetManager(redis)

        assert await manager.consume_token("invalid-token") is None


@pytest.mark.asyncio
async def test_tokens_are_unique():
    async with fakeredis.aioredis.FakeRedis() as redis:
        manager = PasswordResetManager(redis)

        first = await manager.create_token("user-123")
        second = await manager.create_token("user-123")

        assert first != second


@pytest.mark.asyncio
async def test_only_token_hash_stored_in_redis():
    async with fakeredis.aioredis.FakeRedis() as redis:
        manager = PasswordResetManager(redis)

        token = await manager.create_token("user-123")

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        keys = await redis.keys("auth:password_reset:*")

        assert len(keys) == 1
        assert keys[0].decode() == (
            f"auth:password_reset:{token_hash}"
        )
        assert token.encode() not in keys[0]


@pytest.mark.asyncio
async def test_token_has_expiration():
    async with fakeredis.aioredis.FakeRedis() as redis:
        manager = PasswordResetManager(redis)

        token = await manager.create_token(
            "user-123",
            ttl_seconds=900,
        )

        key = manager._token_key(token)
        ttl = await redis.ttl(key)

        assert 0 < ttl <= 900


@pytest.mark.asyncio
async def test_expired_token_rejected():
    async with fakeredis.aioredis.FakeRedis() as redis:
        manager = PasswordResetManager(redis)

        token = await manager.create_token(
            "user-123",
            ttl_seconds=900,
        )

        # Simulate token expiry without waiting 15 minutes.
        await redis.delete(manager._token_key(token))

        assert await manager.consume_token(token) is None


@pytest.mark.asyncio
async def test_invalid_configuration_rejected():
    async with fakeredis.aioredis.FakeRedis() as redis:
        manager = PasswordResetManager(redis)

        with pytest.raises(ValueError):
            await manager.create_token("")

        with pytest.raises(ValueError):
            await manager.create_token(
                "user-123",
                ttl_seconds=0,
            )

        with pytest.raises(ValueError):
            await manager.consume_token("")
