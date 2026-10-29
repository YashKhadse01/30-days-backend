import asyncio
import time
import httpx

BASE_URL = "https://jsonplaceholder.typicode.com"

async def fetch_data(
    client: httpx.AsyncClient,
    endpoint: str,
) -> dict[str, object] | list[object]:
    print(f"Fetching: {endpoint}")

    response = await client.get(endpoint)
    response.raise_for_status()

    data = response.json()

    print(f"Completed: {endpoint}")

    return data

async def main() -> None:
    start = time.perf_counter()

    try:
        async with httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=10.0,
        ) as client:

            users, posts, comments = await asyncio.gather(
                fetch_data(client, "/users"),
                fetch_data(client, "/posts"),
                fetch_data(client, "/comments"),
            )

        print("\nAPI Results:")
        print(f"Total Users: {len(users)}")
        print(f"Total Posts: {len(posts)}")
        print(f"Total Comments: {len(comments)}")
    except httpx.HTTPError as error:
        print(f"API request failed: {error}")
    end = time.perf_counter()
    print(f"\nTotal execution time: {end - start:.2f} seconds")
if __name__ == "__main__":
    asyncio.run(main())
