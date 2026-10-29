import asyncio
import time
async def fetch_data(api_name: str, delay: int) -> str:
    print(f"Fetching data from {api_name}...")

    await asyncio.sleep(delay)

    print(f"Data received from {api_name}")

    return f"{api_name}: Success"
async def main() -> None:
    start = time.perf_counter()

    # Schedule three concurrent tasks
    task1 = asyncio.create_task(
        fetch_data("Users API", 2)
    )

    task2 = asyncio.create_task(
        fetch_data("Products API", 3)
    )

    task3 = asyncio.create_task(
        fetch_data("Orders API", 1)
    )

    # Wait for all tasks and collect their results
    results = await asyncio.gather(
        task1,
        task2,
        task3
    )

    print("\nAPI Results:")

    for result in results:
        print(result)

    end = time.perf_counter()

    print(f"\nTotal execution time: {end - start:.2f} seconds")
if __name__ == "__main__":
    asyncio.run(main())

#Run async_tasks.py and verify that all three API simulations finish in approximately three seconds.
#Then change the Orders API delay from 1 to 5 and observe how the total time changes.


import asyncio
import time


async def fetch_data(api_name: str, delay: int) -> str:
    print(f"Fetching data from {api_name}...")

    # Simulate an asynchronous API request
    await asyncio.sleep(delay)

    print(f"Data received from {api_name}")

    return f"{api_name}: Success"


async def main() -> None:
    start = time.perf_counter()

    # Create three asynchronous tasks
    task1 = asyncio.create_task(
        fetch_data("Users API", 2)
    )

    task2 = asyncio.create_task(
        fetch_data("Products API", 3)
    )

    task3 = asyncio.create_task(
        fetch_data("Orders API", 5)
    )

    # Wait for all tasks to complete
    results = await asyncio.gather(
        task1,
        task2,
        task3
    )

    print("\nAPI Results:")

    for result in results:
        print(result)

    end = time.perf_counter()

    print(f"\nTotal execution time: {end - start:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
