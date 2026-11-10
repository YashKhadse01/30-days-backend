
import json
import time
from enum import Enum

from redis.asyncio import Redis


class AuditEvent(str, Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    ACCOUNT_LOCKED = "account_locked"
    RATE_LIMITED = "rate_limited"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"
    LOGOUT = "logout"


class AuditLogger:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def log(
        self,
        event: AuditEvent,
        *,
        user_id: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        if not isinstance(event, AuditEvent):
            raise ValueError("Invalid audit event")

        # Only explicitly approved fields are recorded.
        record = {
            "event": event.value,
            "user_id": user_id,
            "ip_address": ip_address,
            "timestamp": time.time(),
        }

        await self.redis.rpush(
            "auth:audit_log",
            json.dumps(record),
        )

    async def get_recent(
        self,
        limit: int = 20,
    ) -> list[dict]:
        if limit <= 0:
            raise ValueError("Limit must be positive")

        records = await self.redis.lrange(
            "auth:audit_log",
            -limit,
            -1,
        )

        return [
            json.loads(record)
            for record in reversed(records)
        ]
