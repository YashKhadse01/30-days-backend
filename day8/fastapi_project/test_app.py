import pytest
from fastapi.testclient import TestClient
from practice_api import app, tasks
import practice_api as app_module

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_tasks():
    tasks.clear()
    app_module.next_id = 1
    yield
    tasks.clear()
    app_module.next_id = 1

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Learn FastAPI",
            "priority": 3,
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["title"] == "Learn FastAPI"

def test_get_tasks():
    client.post(
        "/tasks",
        json={"title": "Learn Python", "priority": 3},
    )

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1

def test_search_by_priority():
    client.post(
        "/tasks",
        json={"title": "Learn Python", "priority": 3},
    )
    client.post(
        "/tasks",
        json={"title": "Learn SQL", "priority": 5},
    )

    response = client.get("/search?priority=3")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Learn Python"

def test_invalid_priority():
    response = client.get("/search?priority=9")

    assert response.status_code == 422

def test_invalid_title():
    response = client.post(
        "/tasks",
        json={"title": "Hi", "priority": 3},
    )

    assert response.status_code == 422

def test_missing_task():
    response = client.get("/tasks/999")

    assert response.status_code == 404