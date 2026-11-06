
from datetime import datetime, timedelta, timezone

import pytest

from session_auth_api.sessions import (
    generate_session_token,
    hash_session_token,
    get_session_expiry,
    is_session_expired,
)


def test_generate_session_token():
    token = generate_session_token()

    assert isinstance(token, str)
    assert len(token) >= 40


def test_session_tokens_are_unique():
    token1 = generate_session_token()
    token2 = generate_session_token()

    assert token1 != token2


def test_hash_session_token():
    token = generate_session_token()
    hashed = hash_session_token(token)

    assert len(hashed) == 64
    assert hashed != token


def test_same_token_produces_same_hash():
    token = generate_session_token()

    assert hash_session_token(token) == hash_session_token(token)


def test_different_tokens_produce_different_hashes():
    token1 = generate_session_token()
    token2 = generate_session_token()

    assert hash_session_token(token1) != hash_session_token(token2)


def test_session_expiry_is_in_future():
    expiry = get_session_expiry()

    assert expiry > datetime.now(timezone.utc)


def test_valid_session_not_expired():
    expiry = datetime.now(timezone.utc) + timedelta(hours=1)

    assert is_session_expired(expiry) is False


def test_expired_session():
    expiry = datetime.now(timezone.utc) - timedelta(seconds=1)

    assert is_session_expired(expiry) is True


def test_session_expiring_now():
    expiry = datetime.now(timezone.utc)

    assert is_session_expired(expiry) is True


def test_naive_datetime_rejected():
    expiry = datetime.now()

    with pytest.raises(ValueError, match="timezone-aware"):
        is_session_expired(expiry)
