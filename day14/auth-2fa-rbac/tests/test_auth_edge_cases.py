
import time

import pytest

from auth_2fa_rbac import auth_service as auth
from auth_2fa_rbac.totp import generate_totp_secret, generate_totp


@pytest.fixture
def account():
    """Create isolated authentication state."""
    original_users = auth.users.copy()
    original_sessions = auth.sessions.copy()
    original_challenges = auth.login_challenges.copy()

    auth.users.clear()
    auth.sessions.clear()
    auth.login_challenges.clear()

    secret = generate_totp_secret()

    try:
        auth.create_user(
            username="security_user",
            password="SecureTestPassword123!",
            role="user",
            totp_secret=secret,
        )
        yield secret
    finally:
        auth.users.clear()
        auth.users.update(original_users)

        auth.sessions.clear()
        auth.sessions.update(original_sessions)

        auth.login_challenges.clear()
        auth.login_challenges.update(original_challenges)


def new_challenge():
    challenge = auth.begin_login(
        "security_user",
        "SecureTestPassword123!",
    )
    assert challenge is not None
    return challenge


def test_expired_challenge_rejected(account):
    challenge = new_challenge()

    auth.login_challenges[challenge].expires_at = (
        time.time() - 10
    )

    otp = generate_totp(account)

    assert auth.complete_login(challenge, otp) is None


def test_totp_replay_rejected(account):
    first_challenge = new_challenge()
    otp = generate_totp(account)

    first_session = auth.complete_login(
        first_challenge,
        otp,
    )

    assert first_session is not None

    second_challenge = new_challenge()

    assert auth.complete_login(
        second_challenge,
        otp,
    ) is None


def test_five_failed_2fa_attempts(account):
    challenge = new_challenge()

    correct_otp = generate_totp(account)
    wrong_otp = (
        "000000" if correct_otp != "000000" else "999999"
    )

    for _ in range(auth.MAX_2FA_ATTEMPTS):
        assert auth.complete_login(
            challenge,
            wrong_otp,
        ) is None

    assert challenge not in auth.login_challenges


def test_expired_session_rejected(account):
    challenge = new_challenge()
    otp = generate_totp(account)

    session_token = auth.complete_login(
        challenge,
        otp,
    )

    assert session_token is not None

    username, _ = auth.sessions[session_token]

    auth.sessions[session_token] = (
        username,
        time.time() - 10,
    )

    assert auth.get_session_user(session_token) is None
    assert session_token not in auth.sessions
