#We'll use httpx.MockTransport to simulate API responses, so tests don't depend on your internet connection.

import asyncio
import json
import httpx
import pytest
from api_client import fetch_endpoint

def test_fetch_endpoint_success() -> None:
    """Test successful API response."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {"id": 1, "name": "Yash"},
                {"id": 2, "name": "Rahul"},
            ],
        )

    async def run_test() -> None:
        transport = httpx.MockTransport(handler)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="https://example.com",
        ) as client:
            result = await fetch_endpoint(client, "/users")

        assert len(result) == 2
        assert result[0]["name"] == "Yash"

    asyncio.run(run_test())

def test_fetch_endpoint_http_error() -> None:
    """Test HTTP error handling."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    async def run_test() -> None:
        transport = httpx.MockTransport(handler)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="https://example.com",
        ) as client:
            with pytest.raises(httpx.HTTPStatusError):
                await fetch_endpoint(client, "/missing")

    asyncio.run(run_test())

def test_fetch_endpoint_invalid_data() -> None:
    """Test response validation."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"message": "Not a list"},
        )

    async def run_test() -> None:
        transport = httpx.MockTransport(handler)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="https://example.com",
        ) as client:
            with pytest.raises(ValueError):
                await fetch_endpoint(client, "/users")

    asyncio.run(run_test())

def test_fetch_endpoint_empty_list() -> None:
    """Test an empty API response."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    async def run_test() -> None:
        transport = httpx.MockTransport(handler)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="https://example.com",
        ) as client:
            result = await fetch_endpoint(client, "/users")

        assert result == []

    asyncio.run(run_test())

def test_fetch_endpoint_invalid_json() -> None:
    """Test malformed JSON response."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"invalid json",
        )

    async def run_test() -> None:
        transport = httpx.MockTransport(handler)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="https://example.com",
        ) as client:
            with pytest.raises(json.JSONDecodeError):
                await fetch_endpoint(client, "/users")

    asyncio.run(run_test())
    
from unittest.mock import patch
from api_client import fetch_all_data

def test_fetch_all_data() -> None:
    """Test concurrent API data aggregation."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/users":
            return httpx.Response(
                200,
                json=[{"id": 1}, {"id": 2}],
            )

        if request.url.path == "/posts":
            return httpx.Response(
                200,
                json=[{"id": 1}, {"id": 2}, {"id": 3}],
            )

        if request.url.path == "/comments":
            return httpx.Response(
                200,
                json=[{"id": 1}],
            )

        return httpx.Response(404)

    original_client = httpx.AsyncClient

    def mock_client(*args: object, **kwargs: object) -> httpx.AsyncClient:
        kwargs["transport"] = httpx.MockTransport(handler)
        return original_client(*args, **kwargs)

    with patch("api_client.httpx.AsyncClient", side_effect=mock_client):
        result = asyncio.run(fetch_all_data())

    assert result == {
        "users": 2,
        "posts": 3,
        "comments": 1,
    }
