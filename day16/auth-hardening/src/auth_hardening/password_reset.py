
import hashlib
import secrets

from redis.asyncio import Redis


RESET_TOKEN_TTL_SECONDS = 900

# Atomically read and consume the reset token.
CONSUME_TOKEN_SCRIPT = """
local value = redis.call("GET", KEYS[1])

if not value then
    return nil
end

redis.call("DEL", KEYS[1])

return value
"""


class PasswordResetManager:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _token_key(token: str) -> str:
        if not isinstance(token, str) or not token:
            raise ValueError("Reset token required")

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        return f"auth:password_reset:{token_hash}"

    async def create_token(
        self,
        user_id: str,
        *,
        ttl_seconds: int = RESET_TOKEN_TTL_SECONDS,
    ) -> str:
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("User ID required")

        if ttl_seconds <= 0:
            raise ValueError("TTL must be positive")

        token = secrets.token_urlsafe(32)
        key = self._token_key(token)

        await self.redis.set(
            key,
            user_id,
            ex=ttl_seconds,
            nx=True,
        )

        return token

    async def consume_token(
        self,
        token: str,
    ) -> str | None:
        key = self._token_key(token)

        user_id = await self.redis.eval(
            CONSUME_TOKEN_SCRIPT,
            1,
            key,
        )

        if user_id is None:
            return None

        if isinstance(user_id, bytes):
            return user_id.decode("utf-8")

        return str(user_id)
