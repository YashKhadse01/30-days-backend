
import multiprocessing
import os
import time
def calculate_sum(limit: int) -> int:
    """Perform CPU-intensive calculations."""
    total = 0
    for number in range(limit):
        total += number * number
    return total
def run_sequential(tasks: list[int]) -> list[int]:
    results = []
    for task in tasks:
        results.append(calculate_sum(task))
    return results
def run_parallel(tasks: list[int]) -> list[int]:
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(calculate_sum, tasks)
    return results
def main() -> None:
    tasks = [5_000_000] * 4
    print(f"Available CPU cores: {os.cpu_count()}")
    print("\nRunning sequential execution...")
    start = time.perf_counter()
    sequential_results = run_sequential(tasks)
    sequential_time = time.perf_counter() - start
    print(f"Sequential time: {sequential_time:.2f} seconds")
    print("\nRunning multiprocessing...")
    start = time.perf_counter()
    parallel_results = run_parallel(tasks)
    parallel_time = time.perf_counter() - start
    print(f"Multiprocessing time: {parallel_time:.2f} seconds")
    assert sequential_results == parallel_results
    print("\nBoth approaches produced identical results!")
    if parallel_time > 0:
        speedup = sequential_time / parallel_time
        print(f"Speedup: {speedup:.2f}x")
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

#Run the benchmark and observe these three values:
#- Sequential execution time
#- Multiprocessing execution time
#- Speedup factor
#Try changing 5_000_000 to 10_000_000 and see how the comparison changes.

import multiprocessing
import os
import time
def calculate_sum(limit: int) -> int:
    total = 0
    for number in range(limit):
        total += number * number
    return total
def run_sequential(tasks: list[int]) -> list[int]:
    results = []
    for task in tasks:
        result = calculate_sum(task)
        results.append(result)
    return results
def run_multiprocessing(tasks: list[int]) -> list[int]:
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(calculate_sum, tasks)
    return results
def main() -> None:
    tasks = [10_000_000] * 4
    print(f"Available CPU cores: {os.cpu_count()}")
    # Sequential execution
    print("\nStarting sequential execution...")
    start = time.perf_counter()
    sequential_results = run_sequential(tasks)
    sequential_time = time.perf_counter() - start
    print(f"Sequential time: {sequential_time:.2f} seconds")
    # Multiprocessing execution
    print("\nStarting multiprocessing execution...")
    start = time.perf_counter()
    multiprocessing_results = run_multiprocessing(tasks)
    multiprocessing_time = time.perf_counter() - start
    print(
        f"Multiprocessing time: "
        f"{multiprocessing_time:.2f} seconds"
    )
    # Verify correctness
    assert sequential_results == multiprocessing_results
    print("\nBoth approaches produced identical results!")
    # Calculate speedup
    if multiprocessing_time > 0:
        speedup = sequential_time / multiprocessing_time
        print(f"Speedup: {speedup:.2f}x")
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
