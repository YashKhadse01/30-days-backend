"""Third-party API integration with controlled HTTP requests."""

from typing import Any

import httpx

POSTS_API_URL = "https://jsonplaceholder.typicode.com/posts"


class ExternalAPIError(Exception):
    """The external API returned an invalid or unavailable response."""


async def fetch_external_post(
    post_id: int,
    *,
    client: httpx.AsyncClient,
) -> dict[str, Any]:
    """Fetch and validate a post from a public third-party API."""
    if post_id <= 0:
        raise ValueError("Post ID must be positive")

    try:
        response = await client.get(
            f"{POSTS_API_URL}/{post_id}",
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
    except (
        httpx.HTTPError,
        ValueError,
    ) as exc:
        raise ExternalAPIError(
            "Unable to retrieve a valid external API response"
        ) from exc

    if not isinstance(payload, dict):
        raise ExternalAPIError("External API returned invalid data")

    required_fields = {
        "userId": int,
        "id": int,
        "title": str,
        "body": str,
    }

    for field, expected_type in required_fields.items():
        if type(payload.get(field)) is not expected_type:
            raise ExternalAPIError(
                f"External API response is missing valid {field}"
            )

    if payload["id"] != post_id:
        raise ExternalAPIError("External API returned the wrong post")

    return {
        "id": payload["id"],
        "user_id": payload["userId"],
        "title": payload["title"],
        "body": payload["body"],
    }
