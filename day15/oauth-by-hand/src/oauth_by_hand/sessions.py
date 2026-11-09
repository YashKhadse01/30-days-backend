
import secrets
import time
from dataclasses import dataclass


SESSION_TTL_SECONDS = 1800


@dataclass
class Session:
    user_id: str
    expires_at: float


sessions: dict[str, Session] = {}


def create_session(user_id: str) -> str:
    """Create a secure, temporary application session."""
    if not isinstance(user_id, str) or not user_id:
        raise ValueError("Valid user ID required")

    token = secrets.token_urlsafe(32)

    sessions[token] = Session(
        user_id=user_id,
        expires_at=time.time() + SESSION_TTL_SECONDS,
    )

    return token


def get_session_user_id(token: str) -> str | None:
    """Return user ID for an active session."""
    if not isinstance(token, str) or not token:
        return None

    session = sessions.get(token)

    if session is None:
        return None

    if time.time() >= session.expires_at:
        sessions.pop(token, None)
        return None

    return session.user_id


def revoke_session(token: str) -> None:
    """Invalidate an application session."""
    sessions.pop(token, None)
