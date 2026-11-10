
import time

from redis.asyncio import Redis


LOCKOUT_SCRIPT = """
local attempts_key = KEYS[1]
local lock_key = KEYS[2]
local max_attempts = tonumber(ARGV[1])
local attempt_window = tonumber(ARGV[2])
local lock_seconds = tonumber(ARGV[3])

if redis.call("EXISTS", lock_key) == 1 then
    return 1
end

local attempts = redis.call("INCR", attempts_key)

if attempts == 1 then
    redis.call("EXPIRE", attempts_key, attempt_window)
end

if attempts >= max_attempts then
    redis.call("SET", lock_key, "1", "EX", lock_seconds)
    redis.call("DEL", attempts_key)
    return 1
end

return 0
"""


class BruteForceProtector:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _keys(account: str) -> tuple[str, str]:
        account = account.strip().casefold()

        if not account:
            raise ValueError("Account identifier required")

        return (
            f"auth:failures:{account}",
            f"auth:locked:{account}",
        )

    async def is_locked(self, account: str) -> bool:
        _, lock_key = self._keys(account)
        return bool(await self.redis.exists(lock_key))

    async def record_failure(
        self,
        account: str,
        *,
        max_attempts: int = 5,
        attempt_window_seconds: int = 300,
        lock_seconds: int = 300,
    ) -> bool:
        if min(
            max_attempts,
            attempt_window_seconds,
            lock_seconds,
        ) <= 0:
            raise ValueError("Security settings must be positive")

        attempts_key, lock_key = self._keys(account)

        result = await self.redis.eval(
            LOCKOUT_SCRIPT,
            2,
            attempts_key,
            lock_key,
            max_attempts,
            attempt_window_seconds,
            lock_seconds,
        )

        return bool(result)

    async def record_success(self, account: str) -> None:
        attempts_key, _ = self._keys(account)
        await self.redis.delete(attempts_key)
