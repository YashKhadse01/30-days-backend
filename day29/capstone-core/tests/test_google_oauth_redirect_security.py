"""Security tests for the actual Google OAuth authorization redirect."""

import base64
import hashlib
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from capstone_core.main import create_app


def test_google_redirect_has_state_nonce_and_pkce() -> None:
    """Verify the authorization URL and persisted OAuth state."""
    from capstone_core.core.config import get_settings

    settings = get_settings().model_copy(
        update={
            "google_client_id": "test-google-client",
            "google_client_secret": "test-google-secret",
            "oauth_session_secret": "test-session-secret-" + "x" * 40,
            "google_redirect_uri": (
                "http://127.0.0.1:8765/auth/google/callback"
            ),
        }
    )

    metadata = {
        "issuer": "https://accounts.google.com",
        "authorization_endpoint": (
            "https://accounts.google.com/o/oauth2/v2/auth"
        ),
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
    }

    with patch(
        "capstone_core.main.get_settings",
        return_value=settings,
    ), patch(
        "capstone_core.api.google_oauth.get_settings",
        return_value=settings,
    ), patch(
        "authlib.integrations.base_client.sync_app.OAuth2Mixin.load_server_metadata",
        return_value=metadata,
    ), TestClient(create_app(), follow_redirects=False) as client:
        response = client.get("/auth/google/login")

    assert response.status_code == 302

    parsed = urlparse(response.headers["location"])
    params = parse_qs(parsed.query)

    assert parsed.scheme == "https"
    assert parsed.netloc == "accounts.google.com"
    assert params["client_id"] == ["test-google-client"]
    assert params["response_type"] == ["code"]
    assert params["redirect_uri"] == [
        "http://127.0.0.1:8765/auth/google/callback"
    ]

    scopes = set(params["scope"][0].split())
    assert {"openid", "email", "profile"} <= scopes

    state = params["state"][0]
    nonce = params["nonce"][0]

    assert len(state) >= 20
    assert len(nonce) >= 20

    assert params["code_challenge_method"] == ["S256"]
    challenge = params["code_challenge"][0]

    session_cookie = response.cookies.get("capstone_oauth_session")
    assert session_cookie is not None

    from itsdangerous import TimestampSigner

    signer = TimestampSigner(
        settings.oauth_session_secret
    )

    signed_data = signer.unsign(session_cookie, max_age=600)
    session_data = base64.b64decode(signed_data)

    import json

    session = json.loads(session_data)

    state_key = f"_state_google_{state}"
    assert state_key in session

    authorization_data = session[state_key]["data"]

    assert authorization_data["nonce"] == nonce

    verifier = authorization_data["code_verifier"]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()

    expected_challenge = base64.urlsafe_b64encode(
        digest
    ).rstrip(b"=").decode("ascii")

    assert challenge == expected_challenge
