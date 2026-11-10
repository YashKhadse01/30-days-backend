
import secrets
import time

from redis.asyncio import Redis


SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[4]

redis.call("ZREMRANGEBYSCORE", key, "-inf", now - window)

local count = redis.call("ZCARD", key)

if count >= limit then
    return 0
end

redis.call("ZADD", key, now, member)
redis.call("PEXPIRE", key, math.ceil(window))

return 1
"""


class SlidingWindowRateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def allow(
        self,
        key: str,
        *,
        limit: int = 5,
        window_seconds: int = 60,
    ) -> bool:
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("Limit and window must be positive")

        now_ms = int(time.time() * 1000)
        window_ms = window_seconds * 1000

        result = await self.redis.eval(
            SLIDING_WINDOW_SCRIPT,
            1,
            f"rate_limit:{key}",
            now_ms,
            window_ms,
            limit,
            secrets.token_hex(16),
        )

        return bool(result)
