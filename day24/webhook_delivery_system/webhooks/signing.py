
import hashlib
import hmac
import time

SIGNATURE_TOLERANCE_SECONDS = 300


def create_signature(
    secret: str,
    timestamp: str,
    payload: bytes,
) -> str:
    """Create an HMAC-SHA256 signature over timestamp and raw body."""
    message = timestamp.encode("utf-8") + b"." + payload

    return hmac.new(
        secret.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()


def verify_signature(
    secret: str,
    timestamp: str,
    payload: bytes,
    signature: str,
    *,
    now: int | None = None,
) -> bool:
    """Verify signature and reject expired or future timestamps."""
    try:
        parsed_timestamp = int(timestamp)
    except (TypeError, ValueError):
        return False

    current_time = int(time.time()) if now is None else now

    if abs(current_time - parsed_timestamp) > SIGNATURE_TOLERANCE_SECONDS:
        return False

    expected = create_signature(secret, timestamp, payload)

    return hmac.compare_digest(expected, signature)
