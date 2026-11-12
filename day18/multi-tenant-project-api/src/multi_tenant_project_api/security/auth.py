
from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a password securely using Argon2."""
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a password against its stored hash."""
    return password_hasher.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user_id: str,
    secret_key: str,
    expires_minutes: int = 30,
) -> str:
    """Create a signed, expiring JWT access token."""

    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "type": "access",
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
    secret_key: str,
) -> str | None:
    """Validate JWT and return its user ID."""

    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp", "iat"]},
        )

        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")

        if not isinstance(user_id, str) or not user_id:
            return None

        return user_id

    except InvalidTokenError:
        return None
