
import json
from typing import Any, Awaitable, Callable

from redis.asyncio import Redis


class CacheAsideManager:
    """Redis cache-aside implementation."""

    def __init__(
        self,
        redis: Redis,
        ttl_seconds: int = 60,
    ):
        if ttl_seconds <= 0:
            raise ValueError("TTL must be positive")

        self.redis = redis
        self.ttl_seconds = ttl_seconds

    async def get_or_load(
        self,
        key: str,
        loader: Callable[[], Awaitable[Any]],
    ) -> tuple[Any, bool]:
        """
        Retrieve cached data or load it.

        Returns:
            (data, cache_hit)
        """
        if not key.strip():
            raise ValueError("Cache key is required")

        cached = await self.redis.get(key)

        if cached is not None:
            return json.loads(cached), True

        data = await loader()

        if data is not None:
            await self.redis.set(
                key,
                json.dumps(data),
                ex=self.ttl_seconds,
            )

        return data, False

    async def invalidate(self, key: str) -> bool:
        """Remove a cached entry."""
        if not key.strip():
            raise ValueError("Cache key is required")

        deleted = await self.redis.delete(key)
        return deleted > 0

    async def set_value(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Store a value with an expiration time."""
        if not key.strip():
            raise ValueError("Cache key is required")

        await self.redis.set(
            key,
            json.dumps(value),
            ex=self.ttl_seconds,
        )
