"""Versioned public API with API-key authentication."""

import hashlib
import hmac
import re
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Response,
    Security,
    status,
)
from fastapi.security import APIKeyHeader
from redis.asyncio import Redis
from redis.exceptions import RedisError

from capstone_core.core.config import get_settings
from capstone_core.services.idempotency import (
    IdempotencyConflictError,
    IdempotencyInProgressError,
    RedisIdempotency,
)
from capstone_core.services.rate_limit import RedisRateLimiter

router = APIRouter(prefix="/api/v1", tags=["Public API"])

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="API key issued by the service operator.",
)


def require_api_key(
    api_key: Annotated[str | None, Security(api_key_header)],
) -> None:
    configured_hash = get_settings().api_key_sha256

    if not configured_hash:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API-key authentication is not configured",
        )

    if not re.fullmatch(r"[0-9a-fA-F]{64}", configured_hash):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API-key authentication is misconfigured",
        )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    submitted_hash = hashlib.sha256(api_key.encode()).hexdigest()

    if not hmac.compare_digest(
        submitted_hash,
        configured_hash.lower(),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


async def enforce_rate_limit(
    api_key: Annotated[str | None, Security(api_key_header)],
) -> None:
    """Limit requests using the authenticated API key."""
    require_api_key(api_key)

    assert api_key is not None

    identity = hashlib.sha256(api_key.encode()).hexdigest()
    redis = Redis.from_url(get_settings().redis_url)

    try:
        limiter = RedisRateLimiter(redis)
        allowed = await limiter.allow(
            identity,
            limit=60,
            window_seconds=60,
        )
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiting service unavailable",
        ) from exc
    finally:
        await redis.aclose()

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": "60"},
        )


@router.get(
    "/catalog",
    dependencies=[Depends(enforce_rate_limit)],
    summary="Retrieve the public catalog",
)
async def get_catalog() -> dict[str, object]:
    """Return a safe demonstration catalog."""
    return {
        "version": "v1",
        "items": [
            {"id": "demo-001", "name": "Sample Item"},
        ],
    }




@router.post(
    "/operations",
    dependencies=[Depends(enforce_rate_limit)],
    status_code=status.HTTP_201_CREATED,
    summary="Create an idempotent demonstration operation",
)
async def create_operation(
    payload: dict[str, object],
    response: Response,
    idempotency_key: Annotated[str, Header(min_length=1, max_length=128)],
) -> dict[str, object]:
    """Create or replay a demonstration result without external side effects."""
    redis = Redis.from_url(get_settings().redis_url)

    try:
        service = RedisIdempotency(redis)
        acquired = await service.acquire(idempotency_key, payload)

        if not acquired:
            result = await service.get_result(idempotency_key)
            if result is None:
                raise HTTPException(
                    status_code=409,
                    detail="Completed result is unavailable",
                )
            response.status_code = 200
            return result

        result = {
            "operation_id": idempotency_key,
            "payload": payload,
            "status": "created",
        }

        await service.complete(idempotency_key, payload, result)
        return result

    except (IdempotencyConflictError, IdempotencyInProgressError) as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
    except RedisError as exc:
        raise HTTPException(
            status_code=503,
            detail="Idempotency service unavailable",
        ) from exc
    finally:
        await redis.aclose()
