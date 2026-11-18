
import json
import time

import requests

from webhooks.signing import create_signature


def send_webhook(
    *,
    url: str,
    secret: str,
    event_id: str,
    event_type: str,
    payload: dict,
) -> requests.Response:
    """Send one HMAC-signed webhook HTTP request."""

    body = json.dumps(
        {
            "id": event_id,
            "type": event_type,
            "data": payload,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    timestamp = str(int(time.time()))
    signature = create_signature(
        secret,
        timestamp,
        body,
    )

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-ID": event_id,
        "X-Webhook-Timestamp": timestamp,
        "X-Webhook-Signature": signature,
    }

    return requests.post(
        url,
        data=body,
        headers=headers,
        timeout=(3, 10),
        allow_redirects=False,
    )
