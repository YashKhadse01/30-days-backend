
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from session_auth_api.database import settings


SESSION_TOKEN_BYTES = 32


def generate_session_token() -> str:
    """Generate a cryptographically secure random session token."""
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(token: str) -> str:
    """Create a SHA-256 hash for database storage."""
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def get_session_expiry() -> datetime:
    """Calculate when a session expires."""
    return datetime.now(timezone.utc) + timedelta(
        hours=settings.session_expire_hours
    )


def is_session_expired(expires_at: datetime) -> bool:
    """Check whether a session has expired."""
    if expires_at.tzinfo is None:
        raise ValueError("Session expiry must be timezone-aware")

    return datetime.now(timezone.utc) >= expires_at
