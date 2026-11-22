"""Tests for third-party API integration."""

import httpx
import pytest

from capstone_core.services.external_api import (
    ExternalAPIError,
    fetch_external_post,
)


def make_client(handler):
    return httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    )


@pytest.mark.asyncio
async def test_fetch_external_post_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url).endswith("/posts/7")

        return httpx.Response(
            200,
            json={
                "userId": 2,
                "id": 7,
                "title": "Example",
                "body": "Example content",
            },
        )

    async with make_client(handler) as client:
        result = await fetch_external_post(7, client=client)

    assert result == {
        "id": 7,
        "user_id": 2,
        "title": "Example",
        "body": "Example content",
    }


@pytest.mark.asyncio
async def test_invalid_post_id() -> None:
    async with make_client(
        lambda request: httpx.Response(200)
    ) as client:
        with pytest.raises(ValueError):
            await fetch_external_post(0, client=client)


@pytest.mark.asyncio
async def test_external_http_error() -> None:
    async with make_client(
        lambda request: httpx.Response(503)
    ) as client:
        with pytest.raises(ExternalAPIError):
            await fetch_external_post(7, client=client)


@pytest.mark.asyncio
async def test_external_invalid_json() -> None:
    async with make_client(
        lambda request: httpx.Response(
            200,
            text="not-json",
        )
    ) as client:
        with pytest.raises(ExternalAPIError):
            await fetch_external_post(7, client=client)


@pytest.mark.asyncio
async def test_external_missing_fields() -> None:
    async with make_client(
        lambda request: httpx.Response(
            200,
            json={"id": 7},
        )
    ) as client:
        with pytest.raises(ExternalAPIError):
            await fetch_external_post(7, client=client)


@pytest.mark.asyncio
async def test_external_wrong_post_id() -> None:
    async with make_client(
        lambda request: httpx.Response(
            200,
            json={
                "userId": 2,
                "id": 99,
                "title": "Example",
                "body": "Example content",
            },
        )
    ) as client:
        with pytest.raises(ExternalAPIError):
            await fetch_external_post(7, client=client)
