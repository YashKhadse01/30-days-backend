
from fastapi.testclient import TestClient

from render_deployment_api.main import app


client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Welcome to Day 28 Render Deployment API"
    )


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_nonexistent_endpoint() -> None:
    response = client.get("/invalid-endpoint")

    assert response.status_code == 404
