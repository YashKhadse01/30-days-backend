
import base64
import json
from typing import Any


def base64url_encode(data: bytes) -> str:
    """Encode bytes as unpadded Base64URL."""
    return (
        base64.urlsafe_b64encode(data)
        .rstrip(b"=")
        .decode("ascii")
    )


def base64url_decode(data: str) -> bytes:
    """Decode unpadded Base64URL into bytes."""
    padding = "=" * (-len(data) % 4)
    return base64.b64decode(
        data + padding,
        altchars=b"-_",
        validate=True,
    )


def json_to_base64url(data: dict[str, Any]) -> str:
    """Serialize a JSON object and encode it."""
    raw = json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return base64url_encode(raw)
