
import time
from unittest.mock import patch

import pytest

from jwt_from_scratch.revocation import TokenRevocationList


@pytest.fixture
def store():
    return TokenRevocationList()


def test_new_token_not_revoked(store):
    assert store.is_revoked("token-123") is False


def test_token_can_be_revoked(store):
    store.revoke("token-123", time.time() + 900)
    assert store.is_revoked("token-123") is True


def test_other_tokens_remain_valid(store):
    store.revoke("token-123", time.time() + 900)
    assert store.is_revoked("token-456") is False


def test_repeated_revocation_is_safe(store):
    expiry = time.time() + 900

    store.revoke("token-123", expiry)
    store.revoke("token-123", expiry)

    assert store.is_revoked("token-123") is True


def test_expired_revocation_is_cleaned(store):
    with patch("jwt_from_scratch.revocation.time.time") as clock:
        clock.return_value = 1000
        store.revoke("token-123", 1010)

        assert store.is_revoked("token-123") is True

        clock.return_value = 1011

        assert store.is_revoked("token-123") is False


def test_expired_token_not_added(store):
    store.revoke("token-123", time.time() - 10)
    assert store.is_revoked("token-123") is False


@pytest.mark.parametrize("jti", ["", None, 123])
def test_invalid_jti_rejected(store, jti):
    with pytest.raises(ValueError):
        store.revoke(jti, time.time() + 900)


@pytest.mark.parametrize(
    "expiry",
    [None, True, "tomorrow", float("nan"), float("inf")],
)
def test_invalid_expiry_rejected(store, expiry):
    with pytest.raises(ValueError):
        store.revoke("token-123", expiry)


def test_longer_revocation_expiry_is_preserved(store):
    now = time.time()

    store.revoke("token-123", now + 900)
    store.revoke("token-123", now + 100)

    assert store.is_revoked("token-123") is True
