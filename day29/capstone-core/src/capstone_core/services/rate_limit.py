"""Atomic Redis-backed fixed-window rate limiting."""

import time

from redis.asyncio import Redis

RATE_LIMIT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""


class RedisRateLimiter:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def allow(
        self,
        identity: str,
        *,
        limit: int = 60,
        window_seconds: int = 60,
    ) -> bool:
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("Rate limit settings must be positive")

        window = int(time.time()) // window_seconds
        key = f"rate:{identity}:{window}"

        count = await self.redis.eval(
            RATE_LIMIT_SCRIPT,
            1,
            key,
            window_seconds * 2,
        )

        return int(count) <= limit
