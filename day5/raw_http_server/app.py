import json
from typing import Any
from urllib.parse import urlsplit

USERS: list[dict[str, Any]] = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]

def handle_request(
    method: str,
    target: str,
    body: bytes = b"",
) -> tuple[int, dict[str, Any]]:
    """Process an HTTP request and return status + JSON data."""

    path = urlsplit(target).path

    if method == "GET" and path == "/":
        return 200, {
            "message": "Welcome to the Raw HTTP JSON API"
        }

    if method == "GET" and path == "/health":
        return 200, {"status": "healthy"}

    if path == "/users":
        if method == "GET":
            return 200, {"users": USERS}

        if method == "POST":
            try:
                data = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return 400, {"error": "Invalid JSON"}

            if not isinstance(data, dict):
                return 400, {"error": "Expected a JSON object"}

            name = data.get("name")

            if not isinstance(name, str) or not name.strip():
                return 400, {
                    "error": "A non-empty name is required"
                }

            user = {
                "id": max(
                    (item["id"] for item in USERS),
                    default=0,
                ) + 1,
                "name": name.strip(),
            }

            USERS.append(user)

            return 201, {"user": user}

        return 405, {"error": "Method not allowed"}

    if path.startswith("/users/"):
        if method != "GET":
            return 405, {"error": "Method not allowed"}

        user_id = path.removeprefix("/users/")

        if user_id.isdigit():
            for user in USERS:
                if user["id"] == int(user_id):
                    return 200, {"user": user}

        return 404, {"error": "User not found"}

    return 404, {"error": "Endpoint not found"}
