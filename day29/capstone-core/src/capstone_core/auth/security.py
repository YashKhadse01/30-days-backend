from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")
    return _password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _password_hash.verify(password, hashed)


def create_access_token(
    subject: str,
    secret_key: str,
    expires_minutes: int = 15,
) -> str:
    if not subject or not secret_key or expires_minutes <= 0:
        raise ValueError("Invalid token configuration")

    now = datetime.now(UTC)

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "type": "access",
    }

    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str, secret_key: str) -> str:
    payload = jwt.decode(
        token,
        secret_key,
        algorithms=[ALGORITHM],
        options={"require": ["sub", "iat", "exp"]},
    )

    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid token type")

    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject:
        raise InvalidTokenError("Invalid token subject")

    return subject


def create_two_factor_challenge(
    subject: str,
    secret_key: str,
    expires_minutes: int = 5,
) -> str:
    """Create a short-lived token that cannot authorize API access."""
    from datetime import datetime, timedelta

    now = datetime.now(UTC)

    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "type": "2fa_challenge",
    }

    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_two_factor_challenge(
    token: str,
    secret_key: str,
) -> str:
    """Validate a 2FA challenge and return its user ID."""
    payload = jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
        options={"require": ["sub", "iat", "exp", "type"]},
    )

    if payload.get("type") != "2fa_challenge":
        raise jwt.InvalidTokenError("Invalid token type")

    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject:
        raise jwt.InvalidTokenError("Invalid token subject")

    return subject
