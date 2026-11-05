import hashlib
import secrets
from datetime import datetime, timedelta, timezone

TOKEN_EXPIRY_MINUTES = 30

def generate_verification_token() -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(32)

def hash_verification_token(token: str) -> str:
    """Hash a token before storing it in PostgreSQL."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def get_token_expiry() -> datetime:
    """Return the UTC expiration time for a token."""
    return datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRY_MINUTES
    )

def is_token_expired(expires_at: datetime) -> bool:
    """Check whether a verification token has expired."""
    if expires_at.tzinfo is None:
        raise ValueError("Token expiry must be timezone-aware")

    return datetime.now(timezone.utc) >= expires_at
