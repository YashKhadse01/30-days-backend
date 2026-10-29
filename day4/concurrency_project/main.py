
import asyncio
import time
import httpx

from api_client import fetch_all_data

async def main() -> None:
    start = time.perf_counter()

    try:
        results = await fetch_all_data()

        print("\n=== Async API Data Aggregator ===")
        print(f"Total Users: {results['users']}")
        print(f"Total Posts: {results['posts']}")
        print(f"Total Comments: {results['comments']}")

    except (httpx.HTTPError, ValueError) as error:
        print(f"Failed to fetch API data: {error}")

    finally:
        elapsed = time.perf_counter() - start
        print(f"\nExecution time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
