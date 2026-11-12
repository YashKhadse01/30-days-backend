
import hashlib
import secrets
from datetime import datetime, timedelta, timezone


INVITATION_EXPIRY_HOURS = 24


def generate_invitation_token() -> tuple[str, str]:
    """
    Generate a secure invitation token.

    Returns:
        raw_token: Sent to the invited user.
        token_hash: Stored in PostgreSQL.
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_invitation_token(raw_token)

    return raw_token, token_hash


def hash_invitation_token(token: str) -> str:
    """Return the SHA-256 hash of a token."""
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def invitation_expiration() -> datetime:
    """Return an expiry timestamp 24 hours from now."""
    return datetime.now(timezone.utc) + timedelta(
        hours=INVITATION_EXPIRY_HOURS
    )


def is_invitation_expired(expires_at: datetime) -> bool:
    """Check whether an invitation has expired."""
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    return datetime.now(timezone.utc) >= expires_at
