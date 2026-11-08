from auth_2fa_rbac.totp import generate_totp
from auth_2fa_rbac.backup_codes import redeem_backup_code
import secrets
import time
from dataclasses import dataclass, field

from auth_2fa_rbac.security import hash_password, verify_password


CHALLENGE_TTL_SECONDS = 300


@dataclass
class User:
    username: str
    password_hash: str
    role: str
    totp_secret: str
    backup_hashes: set[str] = field(default_factory=set)
    last_totp_step: int = -1
    failed_2fa_attempts: int = 0


@dataclass
class LoginChallenge:
    username: str
    expires_at: float


users: dict[str, User] = {}
login_challenges: dict[str, LoginChallenge] = {}


def create_user(
    username: str,
    password: str,
    role: str,
    totp_secret: str,
) -> User:
    if not username or username in users:
        raise ValueError("Invalid or duplicate username")

    if not password or not totp_secret:
        raise ValueError("Password and TOTP secret are required")

    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
        totp_secret=totp_secret,
    )

    users[username] = user
    return user


def begin_login(username: str, password: str) -> str | None:
    user = users.get(username)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    challenge_token = secrets.token_urlsafe(32)

    login_challenges[challenge_token] = LoginChallenge(
        username=username,
        expires_at=time.time() + CHALLENGE_TTL_SECONDS,
    )

    return challenge_token

SESSION_TTL_SECONDS = 1800
MAX_2FA_ATTEMPTS = 5

sessions: dict[str, tuple[str, float]] = {}


def complete_login(
    challenge_token: str,
    otp: str,
) -> str | None:
    """Complete 2FA and issue an authenticated session."""
    challenge = login_challenges.get(challenge_token)

    if challenge is None:
        return None

    if time.time() >= challenge.expires_at:
        login_challenges.pop(challenge_token, None)
        return None

    user = users.get(challenge.username)

    if user is None:
        return None

    if user.failed_2fa_attempts >= MAX_2FA_ATTEMPTS:
        login_challenges.pop(challenge_token, None)
        return None

    now = int(time.time())
    current_step = now // 30
    valid_totp_step = None

    # Allow one adjacent time step for clock drift.
    for step in range(current_step - 1, current_step + 2):
        if step < 0 or step <= user.last_totp_step:
            continue

        expected = generate_totp(
            user.totp_secret,
            timestamp=step * 30,
        )

        if (
            isinstance(otp, str)
            and len(otp) == 6
            and otp.isascii()
            and otp.isdigit()
            and secrets.compare_digest(expected, otp)
        ):
            valid_totp_step = step
            break

    if valid_totp_step is None:
        # Backup codes are an alternative second factor.
        valid_backup = redeem_backup_code(
            otp,
            user.backup_hashes,
        )

        if not valid_backup:
            user.failed_2fa_attempts += 1
            if user.failed_2fa_attempts >= MAX_2FA_ATTEMPTS:
                login_challenges.pop(challenge_token, None)
            return None
    else:
        user.last_totp_step = valid_totp_step

    # The challenge is single-use.
    login_challenges.pop(challenge_token, None)
    user.failed_2fa_attempts = 0

    session_token = secrets.token_urlsafe(32)

    sessions[session_token] = (
        user.username,
        time.time() + SESSION_TTL_SECONDS,
    )

    return session_token


def get_session_user(session_token: str) -> User | None:
    """Return the authenticated user for a valid session."""
    session = sessions.get(session_token)

    if session is None:
        return None

    username, expires_at = session

    if time.time() >= expires_at:
        sessions.pop(session_token, None)
        return None

    return users.get(username)


def logout(session_token: str) -> None:
    """Revoke an authenticated session."""
    sessions.pop(session_token, None)
