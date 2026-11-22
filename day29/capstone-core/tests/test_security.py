from datetime import UTC

import pytest
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from capstone_core.auth.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing() -> None:
    password = "StrongPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_empty_password_rejected() -> None:
    with pytest.raises(ValueError):
        hash_password("")


def test_jwt_round_trip() -> None:
    secret = "test-only-secret-not-for-production"
    token = create_access_token("user-123", secret)

    assert decode_access_token(token, secret) == "user-123"


def test_jwt_wrong_secret_rejected() -> None:
    token = create_access_token("user-123", "correct-secret")

    with pytest.raises(InvalidTokenError):
        decode_access_token(token, "incorrect-secret")


def test_expired_token_rejected() -> None:
    from datetime import datetime, timedelta

    import jwt

    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "user-123",
            "iat": now - timedelta(minutes=30),
            "exp": now - timedelta(minutes=15),
            "type": "access",
        },
        "test-secret",
        algorithm="HS256",
    )

    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token, "test-secret")


def test_invalid_token_type_rejected() -> None:
    import jwt

    token = jwt.encode(
        {
            "sub": "user-123",
            "iat": 1,
            "exp": 4102444800,
            "type": "refresh",
        },
        "test-secret",
        algorithm="HS256",
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token, "test-secret")
