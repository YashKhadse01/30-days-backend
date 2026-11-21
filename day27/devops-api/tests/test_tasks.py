from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from devops_api.database import get_db
from devops_api.main import app
from devops_api.models import Task


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()

    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db

    try:
        yield db
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client(mock_db):
    with TestClient(app) as test_client:
        yield test_client


def make_task(task_id: int = 1) -> Task:
    task = Task(
        id=task_id,
        title="Test background task",
        status="pending",
        created_at=datetime.now(UTC),
    )
    return task


def test_create_task_success(client, mock_db):
    task = make_task()

    async def refresh_task(obj):
        obj.id = task.id
        obj.created_at = task.created_at

    mock_db.refresh.side_effect = refresh_task

    with patch("devops_api.main.process_task.delay") as delay:
        response = client.post(
            "/tasks",
            json={"title": "Test background task"},
        )

    assert response.status_code == 201
    assert response.json()["title"] == "Test background task"
    assert response.json()["status"] == "pending"

    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
    delay.assert_called_once_with(1)


def test_create_task_empty_title(client):
    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422


def test_list_tasks(client, mock_db):
    result = MagicMock()
    result.scalars.return_value.all.return_value = [make_task()]
    mock_db.execute.return_value = result

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 1


def test_get_existing_task(client, mock_db):
    mock_db.get.return_value = make_task()

    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_missing_task(client, mock_db):
    mock_db.get.return_value = None

    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_create_task_celery_unavailable(client, mock_db):
    task = make_task()

    async def refresh_task(obj):
        obj.id = task.id
        obj.created_at = task.created_at

    mock_db.refresh.side_effect = refresh_task

    with patch(
        "devops_api.main.process_task.delay",
        side_effect=OSError("Redis unavailable"),
    ):
        response = client.post(
            "/tasks",
            json={"title": "Test background task"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Task saved, but background processing is unavailable"
    )
