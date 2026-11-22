"""Tests for signed outgoing webhooks."""

import hashlib
import hmac
import json

import httpx
import pytest

from capstone_core.services.webhooks import (
    deliver_webhook,
    sign_payload,
)


def test_signature_matches_hmac_sha256() -> None:
    payload = b'{"event":"created"}'
    secret = "test-secret"

    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    assert sign_payload(payload, secret) == expected


def test_empty_secret_rejected() -> None:
    with pytest.raises(ValueError):
        sign_payload(b"payload", "")


@pytest.mark.asyncio
async def test_webhook_delivery() -> None:
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return httpx.Response(200, json={"received": True})

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        status_code = await deliver_webhook(
            "https://example.com/webhooks",
            "report.created",
            {"report_id": "123"},
            "test-secret",
            client=client,
        )

    assert status_code == 200

    request = captured["request"]
    payload = request.content

    assert json.loads(payload)["event"] == "report.created"

    expected_signature = sign_payload(payload, "test-secret")

    assert request.headers["X-Webhook-Signature"] == (
        f"sha256={expected_signature}"
    )


@pytest.mark.asyncio
async def test_webhook_rejects_http() -> None:
    async with httpx.AsyncClient() as client:
        with pytest.raises(ValueError):
            await deliver_webhook(
                "http://example.com/hook",
                "created",
                {},
                "secret",
                client=client,
            )


@pytest.mark.asyncio
async def test_webhook_rejects_empty_event() -> None:
    async with httpx.AsyncClient() as client:
        with pytest.raises(ValueError):
            await deliver_webhook(
                "https://example.com/hook",
                " ",
                {},
                "secret",
                client=client,
            )


@pytest.mark.asyncio
async def test_webhook_http_failure() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(503)
    )

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await deliver_webhook(
                "https://example.com/hook",
                "created",
                {},
                "secret",
                client=client,
            )
