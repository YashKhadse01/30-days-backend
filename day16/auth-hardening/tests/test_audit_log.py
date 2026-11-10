
import json

import fakeredis.aioredis
import pytest

from auth_hardening.audit_log import AuditEvent, AuditLogger


@pytest.mark.asyncio
async def test_login_success_logged():
    async with fakeredis.aioredis.FakeRedis() as redis:
        logger = AuditLogger(redis)

        await logger.log(
            AuditEvent.LOGIN_SUCCESS,
            user_id="user-123",
            ip_address="192.0.2.10",
        )

        events = await logger.get_recent()

        assert len(events) == 1
        assert events[0]["event"] == "login_success"
        assert events[0]["user_id"] == "user-123"
        assert events[0]["ip_address"] == "192.0.2.10"


@pytest.mark.asyncio
async def test_multiple_security_events_logged():
    async with fakeredis.aioredis.FakeRedis() as redis:
        logger = AuditLogger(redis)

        await logger.log(AuditEvent.LOGIN_FAILURE)
        await logger.log(AuditEvent.ACCOUNT_LOCKED)
        await logger.log(AuditEvent.RATE_LIMITED)

        events = await logger.get_recent()

        assert [event["event"] for event in events] == [
            "rate_limited",
            "account_locked",
            "login_failure",
        ]


@pytest.mark.asyncio
async def test_audit_event_contains_timestamp():
    async with fakeredis.aioredis.FakeRedis() as redis:
        logger = AuditLogger(redis)

        await logger.log(AuditEvent.LOGIN_SUCCESS)

        events = await logger.get_recent()

        assert isinstance(events[0]["timestamp"], float)
        assert events[0]["timestamp"] > 0


@pytest.mark.asyncio
async def test_recent_events_limit():
    async with fakeredis.aioredis.FakeRedis() as redis:
        logger = AuditLogger(redis)

        for _ in range(10):
            await logger.log(AuditEvent.LOGIN_FAILURE)

        events = await logger.get_recent(limit=3)

        assert len(events) == 3


@pytest.mark.asyncio
async def test_invalid_event_rejected():
    async with fakeredis.aioredis.FakeRedis() as redis:
        logger = AuditLogger(redis)

        with pytest.raises(ValueError):
            await logger.log("invalid_event")


@pytest.mark.asyncio
async def test_invalid_limit_rejected():
    async with fakeredis.aioredis.FakeRedis() as redis:
        logger = AuditLogger(redis)

        with pytest.raises(ValueError):
            await logger.get_recent(limit=0)


@pytest.mark.asyncio
async def test_audit_record_contains_only_approved_fields():
    async with fakeredis.aioredis.FakeRedis() as redis:
        logger = AuditLogger(redis)

        await logger.log(
            AuditEvent.PASSWORD_RESET_REQUESTED,
            user_id="user-123",
        )

        raw = await redis.lindex("auth:audit_log", 0)
        record = json.loads(raw)

        assert set(record) == {
            "event",
            "user_id",
            "ip_address",
            "timestamp",
        }

        assert "password" not in record
        assert "token" not in record
        assert "secret" not in record


@pytest.mark.asyncio
async def test_password_reset_and_logout_events():
    async with fakeredis.aioredis.FakeRedis() as redis:
        logger = AuditLogger(redis)

        await logger.log(AuditEvent.PASSWORD_RESET_COMPLETED)
        await logger.log(AuditEvent.LOGOUT)

        events = await logger.get_recent()

        assert events[0]["event"] == "logout"
        assert events[1]["event"] == "password_reset_completed"
