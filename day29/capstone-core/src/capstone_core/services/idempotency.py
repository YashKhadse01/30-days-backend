"""Redis-backed idempotency for repeatable operations."""

import hashlib
import json
import secrets
from typing import Any

from redis.asyncio import Redis


class IdempotencyConflictError(Exception):
    """The same idempotency key was used for different input."""


class IdempotencyInProgressError(Exception):
    """The operation is already being processed."""


COMPLETE_SCRIPT = """
local raw = redis.call('GET', KEYS[1])
if not raw then
    return 0
end
local state = cjson.decode(raw)
if state.status ~= 'processing'
   or state.fingerprint ~= ARGV[1]
   or state.owner ~= ARGV[2] then
    return 0
end
redis.call('SET', KEYS[1], ARGV[3], 'EX', ARGV[4])
return 1
"""


class RedisIdempotency:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self._owners: dict[str, str] = {}

    @staticmethod
    def fingerprint(payload: dict[str, Any]) -> str:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    async def acquire(
        self,
        key: str,
        payload: dict[str, Any],
        *,
        ttl_seconds: int = 3600,
    ) -> bool:
        """Acquire a key once, rejecting conflicting or pending requests."""
        if not key.strip():
            raise ValueError("Idempotency key cannot be empty")

        if ttl_seconds <= 0:
            raise ValueError("TTL must be positive")

        redis_key = f"idempotency:{key}"
        fingerprint = self.fingerprint(payload)

        owner = secrets.token_hex(16)
        state = {
            "fingerprint": fingerprint,
            "status": "processing",
            "owner": owner,
        }

        acquired = await self.redis.set(
            redis_key,
            json.dumps(state),
            nx=True,
            ex=ttl_seconds,
        )

        if acquired:
            self._owners[key] = owner
            return True

        existing_raw = await self.redis.get(redis_key)

        if existing_raw is None:
            raise IdempotencyInProgressError(
                "Idempotency state changed; retry the request"
            )

        existing = json.loads(existing_raw)

        if existing["fingerprint"] != fingerprint:
            raise IdempotencyConflictError(
                "Idempotency key was reused with different input"
            )

        if existing["status"] == "processing":
            raise IdempotencyInProgressError(
                "Operation is already in progress"
            )

        return False

    async def complete(
        self,
        key: str,
        payload: dict[str, Any],
        result: dict[str, Any],
        *,
        ttl_seconds: int = 3600,
    ) -> None:
        """Store the result for later replay."""
        state = {
            "fingerprint": self.fingerprint(payload),
            "status": "completed",
            "result": result,
        }

        owner = self._owners.get(key)
        if owner is None:
            raise IdempotencyInProgressError(
                "Operation ownership has not been acquired"
            )

        completed = await self.redis.eval(
            COMPLETE_SCRIPT,
            1,
            f"idempotency:{key}",
            self.fingerprint(payload),
            owner,
            json.dumps(state),
            ttl_seconds,
        )

        if int(completed) != 1:
            raise IdempotencyInProgressError(
                "Operation ownership was lost"
            )

        self._owners.pop(key, None)

    async def get_result(
        self,
        key: str,
    ) -> dict[str, Any] | None:
        """Retrieve a previously completed operation result."""
        raw = await self.redis.get(f"idempotency:{key}")

        if raw is None:
            return None

        state = json.loads(raw)

        if state["status"] != "completed":
            return None

        return state["result"]
