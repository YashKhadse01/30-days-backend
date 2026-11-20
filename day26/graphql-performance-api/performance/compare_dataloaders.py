
import asyncio
from time import perf_counter

from strawberry.dataloader import DataLoader

from graphql_performance_api.dataloaders import PROJECTS


PROJECT_IDS = [1, 1, 2]
ITERATIONS = 1000


async def direct_lookup():
    """Simulate one independent lookup per task."""
    calls = 0
    results = []

    for project_id in PROJECT_IDS:
        calls += 1
        results.append(PROJECTS.get(project_id))

    return results, calls


async def batched_lookup():
    """Simulate one batch containing unique project IDs."""
    batch_calls = 0

    async def load_batch(keys: list[int]):
        nonlocal batch_calls
        batch_calls += 1
        return [PROJECTS.get(key) for key in keys]

    loader = DataLoader(load_fn=load_batch)

    results = await asyncio.gather(
        *(loader.load(key) for key in PROJECT_IDS)
    )

    return results, batch_calls


async def benchmark(operation):
    start = perf_counter()
    total_calls = 0

    for _ in range(ITERATIONS):
        _, calls = await operation()
        total_calls += calls

    elapsed_ms = (perf_counter() - start) * 1000

    return elapsed_ms, total_calls


async def main():
    direct_results, direct_calls = await direct_lookup()
    batch_results, batch_calls = await batched_lookup()

    assert direct_results == batch_results

    print("Project IDs:", PROJECT_IDS)
    print("Direct lookup calls:", direct_calls)
    print("DataLoader batch calls:", batch_calls)

    direct_ms, direct_total = await benchmark(direct_lookup)
    batch_ms, batch_total = await benchmark(batched_lookup)

    print(f"\nIterations: {ITERATIONS}")
    print(f"Direct lookup time: {direct_ms:.3f} ms")
    print(f"DataLoader time: {batch_ms:.3f} ms")
    print(f"Direct lookup calls total: {direct_total}")
    print(f"DataLoader batch calls total: {batch_total}")


if __name__ == "__main__":
    asyncio.run(main())
