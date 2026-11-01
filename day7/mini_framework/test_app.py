import json
import pytest
from app import Request
from main import app, todos
import main

@pytest.fixture(autouse=True)
def reset_todos():
    """Reset application data before every test."""
    todos.clear()
    main.next_id = 1
    yield
    todos.clear()
    main.next_id = 1

def make_request(method, path, data=None):
    """Create a request and dispatch it through our framework."""
    body = b""

    if data is not None:
        body = json.dumps(data).encode("utf-8")

    request = Request(
        method=method,
        path=path,
        headers={"Content-Type": "application/json"},
        body=body,
    )

    return app.dispatch(request)

def create_sample_todo():
    """Create a todo for tests that require existing data."""
    return make_request(
        "POST",
        "/todos",
        {"title": "Learn Python"},
    )

# ---------- HEALTH ENDPOINT ----------

def test_health():
    response = make_request("GET", "/health")

    assert response.status_code == 200
    assert response.body == {"status": "healthy"}

# ---------- LIST TODOS ----------

def test_list_todos_empty():
    response = make_request("GET", "/todos")

    assert response.status_code == 200
    assert response.body == {"todos": []}

def test_list_todos_after_creation():
    create_sample_todo()

    response = make_request("GET", "/todos")

    assert response.status_code == 200
    assert len(response.body["todos"]) == 1

# ---------- CREATE TODO ----------

def test_create_todo():
    response = create_sample_todo()

    assert response.status_code == 201
    assert response.body["todo"]["id"] == 1
    assert response.body["todo"]["title"] == "Learn Python"
    assert response.body["todo"]["completed"] is False

def test_create_todo_missing_title():
    response = make_request("POST", "/todos", {})

    assert response.status_code == 400
    assert response.body["error"] == "Valid title is required"

def test_create_todo_empty_title():
    response = make_request(
        "POST",
        "/todos",
        {"title": "   "},
    )

    assert response.status_code == 400

def test_create_todo_invalid_title_type():
    response = make_request(
        "POST",
        "/todos",
        {"title": 123},
    )

    assert response.status_code == 400

def test_create_todo_invalid_json_type():
    response = make_request(
        "POST",
        "/todos",
        ["not", "an", "object"],
    )

    assert response.status_code == 400

# ---------- GET SINGLE TODO ----------

def test_get_existing_todo():
    create_sample_todo()

    response = make_request("GET", "/todos/1")

    assert response.status_code == 200
    assert response.body["todo"]["id"] == 1

def test_get_missing_todo():
    response = make_request("GET", "/todos/999")

    assert response.status_code == 404
    assert response.body["error"] == "Todo not found"

# ---------- UPDATE TODO ----------

def test_update_todo_title():
    create_sample_todo()

    response = make_request(
        "PUT",
        "/todos/1",
        {"title": "Learn FastAPI"},
    )

    assert response.status_code == 200
    assert response.body["todo"]["title"] == "Learn FastAPI"

def test_update_todo_completed():
    create_sample_todo()

    response = make_request(
        "PUT",
        "/todos/1",
        {"completed": True},
    )

    assert response.status_code == 200
    assert response.body["todo"]["completed"] is True

def test_update_missing_todo():
    response = make_request(
        "PUT",
        "/todos/999",
        {"title": "Missing"},
    )

    assert response.status_code == 404

def test_update_invalid_title():
    create_sample_todo()

    response = make_request(
        "PUT",
        "/todos/1",
        {"title": ""},
    )

    assert response.status_code == 400

def test_update_invalid_completed():
    create_sample_todo()

    response = make_request(
        "PUT",
        "/todos/1",
        {"completed": "yes"},
    )

    assert response.status_code == 400

# ---------- DELETE TODO ----------

def test_delete_existing_todo():
    create_sample_todo()

    response = make_request("DELETE", "/todos/1")

    assert response.status_code == 200
    assert response.body["message"] == "Todo deleted"

    assert 1 not in todos

def test_delete_missing_todo():
    response = make_request("DELETE", "/todos/999")

    assert response.status_code == 404

# ---------- ROUTING ----------

def test_unknown_route():
    response = make_request("GET", "/unknown")

    assert response.status_code == 404
    assert response.body["error"] == "Route not found"

def test_invalid_dynamic_parameter():
    response = make_request("GET", "/todos/abc")

    assert response.status_code == 404

def test_wrong_http_method():
    response = make_request("POST", "/health")

    assert response.status_code == 404

# ---------- JSON ERRORS ----------

def test_malformed_json():
    request = Request(
        method="POST",
        path="/todos",
        body=b'{"title": invalid}',
    )

    response = app.dispatch(request)

    assert response.status_code == 400
    assert response.body["error"] == "Invalid JSON"
def test_response_serialization():
    from app import Response

    response = Response(
        {"message": "Todo created"},
        status_code=201,
    )

    assert response.to_bytes() == b'{"message": "Todo created"}'
    assert response.status_code == 201

def test_update_todo_rejects_json_array():
    from app import Request
    from main import app

    # Create a todo
    create_request = Request(
        method="POST",
        path="/todos",
        body=b'{"title": "Original Todo"}',
    )

    create_response = app.dispatch(create_request)

    assert create_response.status_code == 201

    todo_id = create_response.body["todo"]["id"]

    # Send a JSON array instead of an object
    update_request = Request(
        method="PUT",
        path=f"/todos/{todo_id}",
        body=b'["Invalid", "JSON", "Array"]',
    )

    response = app.dispatch(update_request)

    assert response.status_code == 400
    assert response.body == {"error": "JSON object required"}