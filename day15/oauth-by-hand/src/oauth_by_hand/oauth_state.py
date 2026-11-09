
import secrets
import time
from dataclasses import dataclass


STATE_TTL_SECONDS = 300


@dataclass
class OAuthState:
    code_verifier: str
    expires_at: float
    browser_binding: str = ""
    nonce: str = ""


pending_states: dict[str, OAuthState] = {}


def create_oauth_state(
    code_verifier: str,
    *,
    browser_binding: str = "",
    nonce: str = "",
) -> str:
    """Create a short-lived, single-use OAuth state."""
    if not code_verifier:
        raise ValueError("Code verifier is required")

    state = secrets.token_urlsafe(32)

    pending_states[state] = OAuthState(
        code_verifier=code_verifier,
        expires_at=time.time() + STATE_TTL_SECONDS,
        browser_binding=browser_binding,
        nonce=nonce,
    )

    return state


def consume_oauth_state(
    state: str,
    *,
    browser_binding: str = "",
) -> str | None:
    """Consume state only when the browser binding matches."""
    if not isinstance(state, str) or not state:
        return None

    saved = pending_states.get(state)

    if saved is None:
        return None

    if time.time() >= saved.expires_at:
        pending_states.pop(state, None)
        return None

    if not secrets.compare_digest(
        saved.browser_binding,
        browser_binding,
    ):
        return None

    pending_states.pop(state, None)
    return saved.code_verifier

def consume_oauth_context(
    state: str,
    *,
    browser_binding: str,
) -> tuple[str, str] | None:
    """Consume OAuth state and return (PKCE verifier, OIDC nonce)."""

    if (
        not isinstance(state, str)
        or not state
        or not isinstance(browser_binding, str)
        or not browser_binding
    ):
        return None

    saved = pending_states.get(state)

    if saved is None:
        return None

    if time.time() >= saved.expires_at:
        pending_states.pop(state, None)
        return None

    if (
        not saved.browser_binding
        or not saved.nonce
        or not secrets.compare_digest(
            saved.browser_binding,
            browser_binding,
        )
    ):
        return None

    pending_states.pop(state, None)

    return saved.code_verifier, saved.nonce
