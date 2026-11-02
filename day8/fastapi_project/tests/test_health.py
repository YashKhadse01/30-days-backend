from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_returns_200():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_health_response_schema():
    response = client.get("/health")

    assert response.headers["content-type"] == "application/json"
    assert isinstance(response.json()["status"], str)

def test_openapi_documentation():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert schema["info"]["title"] == "TaskFlow API"
    assert "/health" in schema["paths"]