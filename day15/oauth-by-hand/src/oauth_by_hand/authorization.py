
import secrets
from urllib.parse import urlencode

from oauth_by_hand.pkce import (
    generate_code_verifier,
    generate_code_challenge,
)
from oauth_by_hand.oauth_state import create_oauth_state


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


def build_google_authorization_url(
    client_id: str,
    redirect_uri: str,
    *,
    browser_binding: str = "",
) -> tuple[str, str]:
    """Build a Google OAuth URL with PKCE, state and nonce."""

    if not client_id or not redirect_uri:
        raise ValueError("Client ID and redirect URI are required")

    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)
    nonce = secrets.token_urlsafe(32)

    state = create_oauth_state(
        verifier,
        browser_binding=browser_binding,
        nonce=nonce,
    )

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }

    authorization_url = (
        f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    )

    return authorization_url, state
