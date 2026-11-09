
import pytest

from oauth_by_hand.account_linking import (
    users,
    google_accounts,
    create_local_user,
    find_google_user,
    login_or_register_google,
    link_google_account,
)


@pytest.fixture(autouse=True)
def reset_accounts():
    users.clear()
    google_accounts.clear()
    yield
    users.clear()
    google_accounts.clear()


def test_create_local_user():
    user = create_local_user("user@example.com")

    assert user.user_id in users
    assert user.email == "user@example.com"


def test_empty_email_rejected():
    with pytest.raises(ValueError):
        create_local_user("")


def test_google_login_creates_account():
    claims = {
        "sub": "google-123",
        "email": "user@example.com",
    }

    user = login_or_register_google(claims)

    assert user.user_id in users
    assert google_accounts["google-123"] == user.user_id


def test_repeat_google_login_returns_same_user():
    claims = {
        "sub": "google-123",
        "email": "user@example.com",
    }

    first = login_or_register_google(claims)
    second = login_or_register_google(claims)

    assert first.user_id == second.user_id
    assert len(users) == 1


def test_google_identity_not_matched_by_email():
    local_user = create_local_user("user@example.com")

    google_user = login_or_register_google({
        "sub": "google-123",
        "email": "user@example.com",
    })

    assert local_user.user_id != google_user.user_id


def test_link_google_to_existing_user():
    local_user = create_local_user("user@example.com")

    linked = link_google_account(
        local_user.user_id,
        {"sub": "google-123"},
    )

    assert linked.user_id == local_user.user_id
    assert find_google_user("google-123") == local_user


def test_duplicate_google_link_rejected():
    first = create_local_user("first@example.com")
    second = create_local_user("second@example.com")

    link_google_account(
        first.user_id,
        {"sub": "google-123"},
    )

    with pytest.raises(ValueError, match="already linked"):
        link_google_account(
            second.user_id,
            {"sub": "google-123"},
        )


def test_unknown_local_user_rejected():
    with pytest.raises(ValueError):
        link_google_account(
            "unknown-user-id",
            {"sub": "google-123"},
        )


def test_missing_google_subject_rejected():
    with pytest.raises(ValueError):
        login_or_register_google({"email": "user@example.com"})


def test_link_missing_subject_rejected():
    local_user = create_local_user("user@example.com")

    with pytest.raises(ValueError):
        link_google_account(local_user.user_id, {})


def test_unknown_google_account_returns_none():
    assert find_google_user("unknown-google-sub") is None
