"""Integration tests for the idempotent operations endpoint."""

import hashlib
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from capstone_core.api import public_api
from capstone_core.main import app

TEST_KEY = "operations-integration-key"


@pytest.fixture
def client(monkeypatch):
    original_settings = public_api.get_settings

    def settings():
        original = original_settings()
        return SimpleNamespace(
            api_key_sha256=hashlib.sha256(
                TEST_KEY.encode()
            ).hexdigest(),
            redis_url=original.redis_url,
        )

    monkeypatch.setattr(public_api, "get_settings", settings)

    limiter = AsyncMock()
    limiter.allow.return_value = True
    monkeypatch.setattr(
        public_api,
        "RedisRateLimiter",
        lambda redis: limiter,
    )

    with TestClient(app) as test_client:
        yield test_client


def test_create_replay_and_conflict(client):
    key = str(uuid.uuid4())
    headers = {
        "X-API-Key": TEST_KEY,
        "Idempotency-Key": key,
    }

    first = client.post(
        "/api/v1/operations",
        json={"amount": 100},
        headers=headers,
    )
    assert first.status_code == 201, first.text

    replay = client.post(
        "/api/v1/operations",
        json={"amount": 100},
        headers=headers,
    )
    assert replay.status_code == 200, replay.text
    assert replay.json() == first.json()

    conflict = client.post(
        "/api/v1/operations",
        json={"amount": 200},
        headers=headers,
    )
    assert conflict.status_code == 409, conflict.text


def test_missing_api_key(client):
    response = client.post(
        "/api/v1/operations",
        json={"amount": 100},
        headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code == 401
