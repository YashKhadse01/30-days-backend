
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest

from jwt_from_scratch.refresh import (
    RefreshTokenStore,
    RefreshTokenError,
    RefreshTokenReuseDetected,
)


@pytest.fixture
def store():
    return RefreshTokenStore()


def test_issue_creates_active_token(store):
    token = store.issue("user123")
    assert store.is_active(token)


def test_tokens_are_unique(store):
    first = store.issue("user123")
    second = store.issue("user123")
    assert first != second


def test_rotation_revokes_old_token(store):
    old = store.issue("user123")
    new = store.rotate(old)

    assert not store.is_active(old)
    assert store.is_active(new)


def test_reuse_detected(store):
    old = store.issue("user123")
    store.rotate(old)

    with pytest.raises(RefreshTokenReuseDetected):
        store.rotate(old)


def test_reuse_revokes_entire_family(store):
    first = store.issue("user123")
    second = store.rotate(first)
    third = store.rotate(second)

    with pytest.raises(RefreshTokenReuseDetected):
        store.rotate(first)

    assert not store.is_active(third)


def test_unknown_token_rejected(store):
    with pytest.raises(RefreshTokenError):
        store.rotate("unknown-token")


def test_manual_revocation(store):
    token = store.issue("user123")
    store.revoke(token)

    assert not store.is_active(token)


def test_expired_token_rejected(store):
    with patch("jwt_from_scratch.refresh.time.time") as clock:
        clock.return_value = 1000

        token = store.issue(
            "user123",
            lifetime_seconds=10,
        )

        clock.return_value = 1011

        assert not store.is_active(token)

        with pytest.raises(RefreshTokenError):
            store.rotate(token)


def test_invalid_issue_parameters(store):
    with pytest.raises(ValueError):
        store.issue("")

    with pytest.raises(ValueError):
        store.issue("user123", lifetime_seconds=0)


def test_invalid_rotation_parameters(store):
    with pytest.raises(RefreshTokenError):
        store.rotate("")

    token = store.issue("user123")

    with pytest.raises(RefreshTokenError):
        store.rotate(token, lifetime_seconds=0)


def test_different_families_are_independent(store):
    first = store.issue("user123")
    other = store.issue("user123")

    store.revoke(first)

    assert not store.is_active(first)
    assert store.is_active(other)


def test_concurrent_rotation_allows_only_one_success(store):
    token = store.issue("user123")

    def rotate_once():
        try:
            return ("success", store.rotate(token))
        except RefreshTokenError:
            return ("rejected", None)

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(
            lambda _: rotate_once(),
            range(2),
        ))

    successes = [
        value for status, value in results
        if status == "success"
    ]

    assert len(successes) == 1

    # The second attempt reuses the rotated token,
    # so the whole family must be revoked.
    assert not store.is_active(successes[0])
