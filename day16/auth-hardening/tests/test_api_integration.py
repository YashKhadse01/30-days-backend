
from fastapi.testclient import TestClient
import secrets
from auth_hardening.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "auth-hardening"


def test_home_endpoint():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200

def test_password_reset_requires_demo_key():
    """Reject password reset requests without authorization."""

    with TestClient(app) as client:
        response = client.post(
            "/demo/password-reset/create",
            json={"user_id": "test-user-123"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"

def test_password_reset_token_single_use(monkeypatch):
    """Verify creation, consumption and replay rejection."""

    demo_key = secrets.token_urlsafe(32)
    monkeypatch.setenv("DAY16_DEMO_KEY", demo_key)

    headers = {"X-Demo-Key": demo_key}

    with TestClient(app) as client:
        # Step 1: Create token
        create_response = client.post(
            "/demo/password-reset/create",
            json={"user_id": "integration-user-123"},
            headers=headers,
        )

        assert create_response.status_code == 200

        token = create_response.json()["reset_token"]
        assert token

        # Step 2: Consume token
        consume_response = client.post(
            "/demo/password-reset/consume",
            json={"token": token},
            headers=headers,
        )

        assert consume_response.status_code == 200
        assert (
            consume_response.json()["user_id"]
            == "integration-user-123"
        )

        # Step 3: Attempt to reuse token
        replay_response = client.post(
            "/demo/password-reset/consume",
            json={"token": token},
            headers=headers,
        )

        assert replay_response.status_code == 400

def test_login_failure_triggers_account_lockout():
    """Five failures lock the account; later attempts are blocked."""

    # Use a unique account to avoid Redis state from earlier tests.
    account = f"integration-{secrets.token_hex(12)}@example.com"

    with TestClient(app) as client:
        statuses = []

        for _ in range(6):
            response = client.post(
                "/demo/login-failure",
                json={"account": account},
            )
            statuses.append(response.status_code)

    assert statuses == [401, 401, 401, 401, 429, 429]

def test_rate_limit_blocks_sixth_request():
    """Verify Redis rate limiting through the FastAPI endpoint."""

    # Use a unique client identity to avoid previous Redis counters.
    client_id = secrets.token_hex(16)

    with TestClient(app) as client:
        statuses = []

        for _ in range(6):
            response = client.get(
                "/demo/rate-limit",
                headers={
                    "X-Forwarded-For": client_id,
                },
            )
            statuses.append(response.status_code)

    assert statuses == [200, 200, 200, 200, 200, 429]


def test_rate_limit_blocks_sixth_request(monkeypatch):
    """Verify five allowed requests and sixth blocked."""

    monkeypatch.setenv("DAY16_TESTING", "1")

    client_id = secrets.token_hex(16)

    with TestClient(app) as client:
        statuses = []

        for _ in range(6):
            response = client.get(
                "/demo/rate-limit",
                headers={
                    "X-Test-Client-ID": client_id,
                },
            )

            statuses.append(response.status_code)

    assert statuses == [
        200,
        200,
        200,
        200,
        200,
        429,
    ]
