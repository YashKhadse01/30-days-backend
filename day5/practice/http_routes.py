import json
import socket
from typing import Any
from urllib.parse import urlsplit

HOST = "127.0.0.1"
PORT = 8001

USERS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"},
]

def route_request(
    method: str,
    path: str,
) -> tuple[int, str, dict[str, Any]]:

    if method != "GET":
        return (
            405,
            "Method Not Allowed",
            {"error": "Only GET requests are supported"},
        )

    if path == "/":
        return (
            200,
            "OK",
            {"message": "Welcome to Day 5 Raw HTTP Server"},
        )

    if path == "/health":
        return (
            200,
            "OK",
            {"status": "healthy"},
        )

    if path == "/users":
        return (
            200,
            "OK",
            {"users": USERS},
        )

    if path.startswith("/users/"):
        user_id = path.removeprefix("/users/")

        if user_id.isdigit():
            for user in USERS:
                if user["id"] == int(user_id):
                    return (200, "OK", {"user": user})

        return (
            404,
            "Not Found",
            {"error": "User not found"},
        )

    return (
        404,
        "Not Found",
        {"error": "Endpoint not found"},
    )

def build_response(
    status_code: int,
    reason: str,
    data: dict[str, Any],
) -> bytes:

    body = json.dumps(data).encode("utf-8")

    headers = (
        f"HTTP/1.1 {status_code} {reason}\r\n"
        "Content-Type: application/json; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8")

    return headers + body

def main() -> None:
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as server:

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )

        server.bind((HOST, PORT))
        server.listen(5)

        print(f"Server running at http://{HOST}:{PORT}")
        print("Press Ctrl+C to stop.")

        while True:
            connection, address = server.accept()

            with connection:
                request = connection.recv(4096)

                if not request:
                    continue

                try:
                    request_line = request.decode(
                        "iso-8859-1"
                    ).split("\r\n", 1)[0]

                    method, target, version = request_line.split()

                    if not version.startswith("HTTP/"):
                        raise ValueError("Invalid HTTP version")

                    path = urlsplit(target).path

                    print(f"{address} -> {method} {path}")

                    status_code, reason, data = route_request(
                        method,
                        path,
                    )

                except (ValueError, UnicodeError):
                    status_code = 400
                    reason = "Bad Request"
                    data = {"error": "Malformed HTTP request"}

                response = build_response(
                    status_code,
                    reason,
                    data,
                )

                connection.sendall(response)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped.")
