"""Signed outgoing webhook delivery."""

import hashlib
import hmac
import json
from typing import Any

import httpx


def sign_payload(payload: bytes, secret: str) -> str:
    """Create an HMAC-SHA256 signature for webhook verification."""
    if not secret:
        raise ValueError("Webhook secret cannot be empty")

    return hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()


async def deliver_webhook(
    url: str,
    event: str,
    data: dict[str, Any],
    secret: str,
    *,
    client: httpx.AsyncClient,
) -> int:
    """Send a signed JSON event to a configured webhook destination."""
    if not url.startswith("https://"):
        raise ValueError("Webhook destination must use HTTPS")

    if not event.strip():
        raise ValueError("Webhook event cannot be empty")

    payload = json.dumps(
        {"event": event, "data": data},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    signature = sign_payload(payload, secret)

    response = await client.post(
        url,
        content=payload,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Event": event,
            "X-Webhook-Signature": f"sha256={signature}",
        },
        timeout=10.0,
    )

    response.raise_for_status()
    return response.status_code
