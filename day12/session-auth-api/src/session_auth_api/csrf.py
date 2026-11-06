from urllib.parse import urlsplit
import hashlib
import hmac
import secrets

from fastapi import HTTPException, Request

CSRF_COOKIE_NAME = "day12_csrf"
CSRF_HEADER_NAME = "X-CSRF-Token"


def generate_csrf_token(
    session_token: str,
    secret_key: str,
) -> str:
    """Create a signed token bound to one login session."""
    nonce = secrets.token_hex(32)

    message = f"{session_token}:{nonce}".encode()

    signature = hmac.new(
        secret_key.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    return f"{nonce}.{signature}"


def validate_csrf_token(
    session_token: str,
    csrf_token: str,
    secret_key: str,
) -> bool:
    """Validate the token's format and HMAC signature."""
    try:
        nonce, signature = csrf_token.split(".")
    except ValueError:
        return False

    if len(nonce) != 64 or len(signature) != 64:
        return False

    try:
        bytes.fromhex(nonce)
        bytes.fromhex(signature)
    except ValueError:
        return False

    message = f"{session_token}:{nonce}".encode()

    expected = hmac.new(
        secret_key.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


def require_csrf(
    request: Request,
    session_token: str,
    secret_key: str,
) -> None:
    """Require matching cookie/header and a valid signature."""
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    header_token = request.headers.get(CSRF_HEADER_NAME)

    if (
        not cookie_token
        or not header_token
        or not hmac.compare_digest(cookie_token, header_token)
        or not validate_csrf_token(
            session_token,
            header_token,
            secret_key,
        )
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid CSRF token",
        )

def validate_request_origin(
    request: Request,
    allowed_origins: set[str],
) -> None:
    """Reject browser requests from untrusted origins."""

    origin = request.headers.get("origin")

    if origin is None:
        referer = request.headers.get("referer")

        if not referer:
            raise HTTPException(
                status_code=403,
                detail="Missing request origin",
            )

        parsed = urlsplit(referer)

        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(
                status_code=403,
                detail="Invalid request origin",
            )

        origin = f"{parsed.scheme}://{parsed.netloc}"

    if origin not in allowed_origins:
        raise HTTPException(
            status_code=403,
            detail="Untrusted request origin",
        )
