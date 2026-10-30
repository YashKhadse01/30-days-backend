import json
import socket
import pytest
from server import build_response, read_request

def test_build_success_response():
    response = build_response(
        200,
        {"status": "healthy"},
    )

    headers, body = response.split(b"\r\n\r\n", 1)

    assert headers.startswith(b"HTTP/1.1 200 OK")
    assert b"Content-Type: application/json" in headers
    assert f"Content-Length: {len(body)}".encode() in headers
    assert json.loads(body) == {"status": "healthy"}

def test_build_created_response():
    response = build_response(
        201,
        {"user": {"id": 3, "name": "Charlie"}},
    )

    assert response.startswith(b"HTTP/1.1 201 Created")

def test_build_unknown_status():
    response = build_response(418, {"message": "Test"})

    assert response.startswith(b"HTTP/1.1 418 Unknown")

def test_read_get_request():
    client, server = socket.socketpair()

    try:
        client.sendall(
            b"GET /health HTTP/1.1\r\n"
            b"Host: localhost\r\n"
            b"\r\n"
        )

        method, target, body = read_request(server)

        assert method == "GET"
        assert target == "/health"
        assert body == b""

    finally:
        client.close()
        server.close()

def test_read_post_request():
    client, server = socket.socketpair()

    try:
        body = b'{"name":"Charlie"}'

        request = (
            b"POST /users HTTP/1.1\r\n"
            b"Host: localhost\r\n"
            + f"Content-Length: {len(body)}\r\n".encode()
            + b"\r\n"
            + body
        )

        client.sendall(request)

        method, target, received_body = read_request(server)

        assert method == "POST"
        assert target == "/users"
        assert received_body == body

    finally:
        client.close()
        server.close()

@pytest.mark.parametrize(
    "raw_request",
    [
        b"INVALID\r\n\r\n",
        b"GET / HTTP/9.9\r\n\r\n",
        b"GET / HTTP/1.1\r\nInvalidHeader\r\n\r\n",
        b"GET / HTTP/1.1\r\nContent-Length: abc\r\n\r\n",
        b"GET / HTTP/1.1\r\nContent-Length: -1\r\n\r\n",
        b"GET / HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n",
        (
            b"GET / HTTP/1.1\r\n"
            b"X-Test: one\r\n"
            b"X-Test: two\r\n\r\n"
        ),
    ],
)
def test_invalid_requests(raw_request):
    client, server = socket.socketpair()

    try:
        client.sendall(raw_request)

        with pytest.raises(ValueError):
            read_request(server)

    finally:
        client.close()
        server.close()

def test_incomplete_headers():
    client, server = socket.socketpair()

    try:
        client.sendall(b"GET / HTTP/1.1\r\n")
        client.shutdown(socket.SHUT_WR)

        with pytest.raises(ValueError, match="Incomplete HTTP headers"):
            read_request(server)
    finally:
        client.close()
        server.close()


def test_incomplete_body():
    client, server = socket.socketpair()

    try:
        client.sendall(
            b"POST /users HTTP/1.1\r\n"
            b"Content-Length: 20\r\n"
            b"\r\n"
            b'{"name":"A"}'
        )
        client.shutdown(socket.SHUT_WR)

        with pytest.raises(ValueError, match="Incomplete request body"):
            read_request(server)
    finally:
        client.close()
        server.close()


def test_oversized_body():
    client, server = socket.socketpair()

    try:
        client.sendall(
            b"POST /users HTTP/1.1\r\n"
            b"Content-Length: 1000001\r\n"
            b"\r\n"
        )

        with pytest.raises(ValueError, match="Invalid body size"):
            read_request(server)
    finally:
        client.close()
        server.close()


def test_http_10_supported():
    client, server = socket.socketpair()

    try:
        client.sendall(b"GET / HTTP/1.0\r\n\r\n")

        method, target, body = read_request(server)

        assert method == "GET"
        assert target == "/"
        assert body == b""
    finally:
        client.close()
        server.close()
