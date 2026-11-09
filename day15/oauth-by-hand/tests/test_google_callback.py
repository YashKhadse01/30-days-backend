
import pytest
from fastapi.testclient import TestClient

import importlib

main = importlib.import_module("oauth_by_hand.main")
from oauth_by_hand.oauth_state import (
    create_oauth_state,
    pending_states,
)
from oauth_by_hand.account_linking import (
    users,
    google_accounts,
)


@pytest.fixture(autouse=True)
def reset_data(monkeypatch):
    pending_states.clear()
    users.clear()
    google_accounts.clear()

    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client")

    yield

    pending_states.clear()
    users.clear()
    google_accounts.clear()


@pytest.fixture
def client():
    return TestClient(main.app)


def create_callback_state():
    return create_oauth_state(
        "test-verifier",
        browser_binding="test-browser",
        nonce="test-nonce",
    )


def test_missing_callback_parameters(client):
    response = client.get("/auth/google/callback")

    assert response.status_code == 400


def test_invalid_state_rejected(client):
    client.cookies.set(
        "oauth_browser_binding",
        "test-browser",
        path="/auth/google",
    )

    response = client.get(
        "/auth/google/callback",
        params={
            "code": "test-code",
            "state": "invalid-state",
        },
    )

    assert response.status_code == 401


def test_wrong_browser_rejected(client):
    state = create_callback_state()

    client.cookies.set(
        "oauth_browser_binding",
        "wrong-browser",
        path="/auth/google",
    )

    response = client.get(
        "/auth/google/callback",
        params={
            "code": "test-code",
            "state": state,
        },
    )

    assert response.status_code == 401


def test_google_denied_authorization(client):
    response = client.get(
        "/auth/google/callback",
        params={"error": "access_denied"},
    )

    assert response.status_code == 400


def test_successful_google_callback(
    client,
    monkeypatch,
):
    state = create_callback_state()

    client.cookies.set(
        "oauth_browser_binding",
        "test-browser",
        path="/auth/google",
    )

    async def fake_exchange(**kwargs):
        assert kwargs["code_verifier"] == "test-verifier"
        return {
            "access_token": "fake-access-token",
            "id_token": "fake-id-token",
        }

    async def fake_verify(token, client_id, *, expected_nonce):
        assert token == "fake-id-token"
        assert client_id == "test-client"
        assert expected_nonce == "test-nonce"

        return {
            "sub": "google-user-123",
            "email": "user@example.com",
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

    response = client.get(
        "/auth/google/callback",
        params={
            "code": "test-code",
            "state": state,
        },
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "google"
    assert response.json()["email"] == "user@example.com"
    assert len(users) == 1
    assert "google-user-123" in google_accounts

    # OAuth state must not be reusable.
    assert state not in pending_states
