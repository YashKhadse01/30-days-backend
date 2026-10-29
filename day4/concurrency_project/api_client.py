#This module will handle API communication and error handling.
import asyncio
from typing import Any
import httpx

BASE_URL = "https://jsonplaceholder.typicode.com"

async def fetch_endpoint(
    client: httpx.AsyncClient,
    endpoint: str,
) -> list[dict[str, Any]]:
    """Fetch JSON data from one API endpoint."""

    response = await client.get(endpoint)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a list from {endpoint}"
        )

    return data

async def fetch_all_data() -> dict[str, int]:
    """Fetch users, posts, and comments concurrently."""

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=10.0,
    ) as client:

        users, posts, comments = await asyncio.gather(
            fetch_endpoint(client, "/users"),
            fetch_endpoint(client, "/posts"),
            fetch_endpoint(client, "/comments"),
        )

    return {
        "users": len(users),
        "posts": len(posts),
        "comments": len(comments),
    }
