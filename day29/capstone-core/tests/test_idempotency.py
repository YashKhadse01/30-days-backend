"""Tests for Redis-backed idempotency."""

import json
from unittest.mock import AsyncMock

import pytest

from capstone_core.services.idempotency import (
    IdempotencyConflictError,
    IdempotencyInProgressError,
    RedisIdempotency,
)


@pytest.mark.asyncio
async def test_first_request_acquires_key() -> None:
    redis = AsyncMock()
    redis.set.return_value = True

    service = RedisIdempotency(redis)

    assert await service.acquire(
        "request-1",
        {"amount": 100},
    )

    assert redis.set.await_args.kwargs["nx"] is True
    assert redis.set.await_args.kwargs["ex"] == 3600


@pytest.mark.asyncio
async def test_duplicate_completed_request() -> None:
    redis = AsyncMock()
    redis.set.return_value = False

    payload = {"amount": 100}
    fingerprint = RedisIdempotency.fingerprint(payload)

    redis.get.return_value = json.dumps(
        {
            "fingerprint": fingerprint,
            "status": "completed",
            "result": {"id": "123"},
        }
    )

    service = RedisIdempotency(redis)

    assert not await service.acquire("request-1", payload)
    assert await service.get_result("request-1") == {"id": "123"}


@pytest.mark.asyncio
async def test_conflicting_payload_rejected() -> None:
    redis = AsyncMock()
    redis.set.return_value = False

    redis.get.return_value = json.dumps(
        {
            "fingerprint": RedisIdempotency.fingerprint(
                {"amount": 100}
            ),
            "status": "completed",
        }
    )

    with pytest.raises(IdempotencyConflictError):
        await RedisIdempotency(redis).acquire(
            "request-1",
            {"amount": 200},
        )


@pytest.mark.asyncio
async def test_processing_request_rejected() -> None:
    redis = AsyncMock()
    redis.set.return_value = False

    payload = {"amount": 100}

    redis.get.return_value = json.dumps(
        {
            "fingerprint": RedisIdempotency.fingerprint(payload),
            "status": "processing",
        }
    )

    with pytest.raises(IdempotencyInProgressError):
        await RedisIdempotency(redis).acquire(
            "request-1",
            payload,
        )


@pytest.mark.asyncio
async def test_completed_result_saved() -> None:
    redis = AsyncMock()
    redis.set.return_value = True
    redis.eval.return_value = 1

    service = RedisIdempotency(redis)
    payload = {"amount": 100}

    assert await service.acquire("request-1", payload)
    await service.complete(
        "request-1",
        payload,
        {"id": "123"},
    )

    state = json.loads(redis.eval.await_args.args[5])

    assert state["status"] == "completed"
    assert state["result"] == {"id": "123"}


@pytest.mark.asyncio
async def test_invalid_idempotency_key_rejected() -> None:
    with pytest.raises(ValueError):
        await RedisIdempotency(AsyncMock()).acquire(
            " ",
            {},
        )


@pytest.mark.asyncio
async def test_invalid_ttl_rejected() -> None:
    with pytest.raises(ValueError):
        await RedisIdempotency(AsyncMock()).acquire(
            "request-1",
            {},
            ttl_seconds=0,
        )
