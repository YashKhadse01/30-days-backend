from datetime import UTC, datetime, timedelta

import jwt
import pytest

from capstone_core.auth.security import (
    create_access_token,
    create_two_factor_challenge,
    decode_two_factor_challenge,
)

SECRET = "test-challenge-signing-secret-at-least-32-bytes"
SUBJECT = "test-user-123"


def test_valid_challenge():
    token = create_two_factor_challenge(SUBJECT, SECRET)

    assert decode_two_factor_challenge(token, SECRET) == SUBJECT


def test_expired_challenge_rejected():
    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": SUBJECT,
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
            "type": "2fa_challenge",
        },
        SECRET,
        algorithm="HS256",
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_two_factor_challenge(token, SECRET)


def test_access_token_rejected_as_challenge():
    token = create_access_token(SUBJECT, SECRET)

    with pytest.raises(jwt.InvalidTokenError):
        decode_two_factor_challenge(token, SECRET)


def test_wrong_signing_key_rejected():
    token = create_two_factor_challenge(SUBJECT, SECRET)

    with pytest.raises(jwt.InvalidSignatureError):
        decode_two_factor_challenge(
            token,
            "different-signing-secret-at-least-32-bytes",
        )


def test_missing_subject_rejected():
    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "type": "2fa_challenge",
        },
        SECRET,
        algorithm="HS256",
    )

    with pytest.raises(jwt.MissingRequiredClaimError):
        decode_two_factor_challenge(token, SECRET)


def test_empty_subject_rejected():
    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": "",
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "type": "2fa_challenge",
        },
        SECRET,
        algorithm="HS256",
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_two_factor_challenge(token, SECRET)


def test_tampered_challenge_rejected():
    token = create_two_factor_challenge(SUBJECT, SECRET)

    header, payload, signature = token.split(".")
    tampered_payload = "A" + payload[1:]
    tampered = f"{header}.{tampered_payload}.{signature}"

    with pytest.raises(jwt.InvalidTokenError):
        decode_two_factor_challenge(tampered, SECRET)
