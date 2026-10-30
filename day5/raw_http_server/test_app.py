import json
import pytest
from app import USERS, handle_request

@pytest.fixture(autouse=True)
def reset_users():
    """Reset user data before and after each test."""
    original_users = [user.copy() for user in USERS]

    USERS.clear()
    USERS.extend([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])

    yield

    USERS.clear()
    USERS.extend(original_users)

def test_home():
    status, data = handle_request("GET", "/")

    assert status == 200
    assert "Welcome" in data["message"]

def test_health():
    status, data = handle_request("GET", "/health")

    assert status == 200
    assert data == {"status": "healthy"}

def test_get_all_users():
    status, data = handle_request("GET", "/users")

    assert status == 200
    assert len(data["users"]) == 2

def test_get_existing_user():
    status, data = handle_request("GET", "/users/1")

    assert status == 200
    assert data["user"]["name"] == "Alice"

def test_create_user():
    body = json.dumps({"name": "Charlie"}).encode("utf-8")

    status, data = handle_request("POST", "/users", body)

    assert status == 201
    assert data["user"]["id"] == 3
    assert data["user"]["name"] == "Charlie"

def test_create_user_with_whitespace():
    body = json.dumps({"name": "  Charlie  "}).encode("utf-8")

    status, data = handle_request("POST", "/users", body)

    assert status == 201
    assert data["user"]["name"] == "Charlie"

def test_invalid_json():
    status, data = handle_request(
        "POST",
        "/users",
        b"invalid json",
    )

    assert status == 400
    assert data["error"] == "Invalid JSON"

def test_invalid_json_encoding():
    status, data = handle_request(
        "POST",
        "/users",
        b"\xff",
    )

    assert status == 400
    assert data["error"] == "Invalid JSON"

def test_json_array_rejected():
    status, data = handle_request(
        "POST",
        "/users",
        b'["Alice"]',
    )

    assert status == 400
    assert data["error"] == "Expected a JSON object"

@pytest.mark.parametrize(
    "body",
    [
        b"{}",
        b'{"name":""}',
        b'{"name":"   "}',
        b'{"name":123}',
    ],
)
def test_invalid_name(body):
    status, data = handle_request("POST", "/users", body)

    assert status == 400
    assert "name" in data["error"]

def test_user_not_found():
    status, data = handle_request("GET", "/users/999")

    assert status == 404
    assert data["error"] == "User not found"

def test_invalid_user_id():
    status, data = handle_request("GET", "/users/abc")

    assert status == 404

def test_unknown_endpoint():
    status, data = handle_request("GET", "/unknown")

    assert status == 404
    assert data["error"] == "Endpoint not found"

def test_unsupported_method_users():
    status, data = handle_request("DELETE", "/users")

    assert status == 405

def test_unsupported_method_user_id():
    status, data = handle_request("DELETE", "/users/1")

    assert status == 405

def test_query_parameters():
    status, data = handle_request("GET", "/users?page=1")

    assert status == 200
    assert len(data["users"]) == 2

def test_empty_user_collection():
    USERS.clear()

    status, data = handle_request("POST", "/users", b'{"name":"First"}')

    assert status == 201
    assert data["user"]["id"] == 1
