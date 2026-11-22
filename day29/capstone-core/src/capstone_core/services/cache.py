"""Redis-backed JSON cache with expiration."""

import json
from typing import Any

from redis.asyncio import Redis


class RedisCache:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> Any | None:
        value = await self.redis.get(f"cache:{key}")

        if value is None:
            return None

        return json.loads(value)

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 300,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("Cache TTL must be positive")

        await self.redis.set(
            f"cache:{key}",
            json.dumps(value),
            ex=ttl_seconds,
        )

    async def delete(self, key: str) -> None:
        await self.redis.delete(f"cache:{key}")
