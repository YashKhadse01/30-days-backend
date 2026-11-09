
import importlib
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from oauth_by_hand.account_linking import (
    google_accounts,
    users,
)
from oauth_by_hand.oauth_state import pending_states
from oauth_by_hand.sessions import sessions


main = importlib.import_module("oauth_by_hand.main")


def test_complete_google_oauth_flow(monkeypatch):
    pending_states.clear()
    sessions.clear()
    users.clear()
    google_accounts.clear()

    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setattr(main, "GOOGLE_CLIENT_ID", "test-client")

    async def fake_exchange(**kwargs):
        assert kwargs["code"] == "mock-code"
        assert kwargs["code_verifier"]
        return {"id_token": "mock-id-token"}

    async def fake_verify(token, client_id, *, expected_nonce):
        assert token == "mock-id-token"
        assert client_id == "test-client"
        assert expected_nonce
        return {
            "sub": "google-test-123",
            "email": "oauth@example.com",
        }

    monkeypatch.setattr(
        main,
        "exchange_google_code",
        fake_exchange,
    )

    monkeypatch.setattr(
        main,
        "verify_google_id_token",
        fake_verify,
    )

    try:
        with TestClient(main.app) as client:

            # Step 1: Start Google OAuth login.
            login = client.get(
                "/auth/google/login",
                follow_redirects=False,
            )

            assert login.status_code == 302

            params = parse_qs(
                urlparse(login.headers["location"]).query
            )

            state = params["state"][0]

            assert state in pending_states
            assert params["code_challenge_method"] == ["S256"]
            assert params["nonce"][0] == pending_states[state].nonce
            assert client.cookies.get("oauth_browser_binding")

            # Step 2: Simulate Google's callback.
            callback = client.get(
                "/auth/google/callback",
                params={
                    "code": "mock-code",
                    "state": state,
                },
            )

            assert callback.status_code == 200
            assert callback.json()["provider"] == "google"
            assert state not in pending_states
            assert client.cookies.get("app_session")

            # Step 3: Access authenticated profile.
            profile = client.get("/auth/me")

            assert profile.status_code == 200
            assert profile.json()["email"] == "oauth@example.com"

            # Step 4: Log out with a valid same-origin header.
            logout = client.post(
                "/auth/logout",
                headers={
                    "Origin": "http://testserver",
                },
            )

            assert logout.status_code == 200
            assert logout.json()["message"] == (
                "Logged out successfully"
            )

            # Step 5: Verify session revocation.
            assert client.cookies.get("app_session") is None

            after_logout = client.get("/auth/me")

            assert after_logout.status_code == 401

    finally:
        pending_states.clear()
        sessions.clear()
        users.clear()
        google_accounts.clear()
