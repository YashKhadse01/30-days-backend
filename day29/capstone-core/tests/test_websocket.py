"""Tests for the real-time WebSocket endpoint."""

from fastapi.testclient import TestClient

from capstone_core.main import app


def test_websocket_echo() -> None:
    client = TestClient(app)

    with client.websocket_connect("/ws/echo") as websocket:
        websocket.send_text("hello")
        assert websocket.receive_json() == {
            "event": "message",
            "data": "hello",
        }

        websocket.send_text("backend")
        assert websocket.receive_json() == {
            "event": "message",
            "data": "backend",
        }


def test_websocket_route_registered() -> None:
    """Verify that the WebSocket endpoint accepts a real connection."""
    client = TestClient(app)

    with client.websocket_connect("/ws/echo") as websocket:
        websocket.send_text("route-check")

        assert websocket.receive_json() == {
            "event": "message",
            "data": "route-check",
        }
