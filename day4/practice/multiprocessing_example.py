import multiprocessing
import time
def calculate_square(number: int) -> None:
    print(f"Starting calculation for {number}")
    result = number * number
    time.sleep(2)  # Simulates waiting, not CPU work
    print(f"Square of {number} = {result}")
def main() -> None:
    start = time.perf_counter()
    processes: list[multiprocessing.Process] = []
    for number in range(1, 6):
        process = multiprocessing.Process(
            target=calculate_square,
            args=(number,)
        )
        processes.append(process)
        process.start()
    for process in processes:
        process.join()
    end = time.perf_counter()
    print(
        f"\nTotal execution time: "
        f"{end - start:.2f} seconds"
    )
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

#Run multiprocessing_example.py and observe how long the five processes take.

import multiprocessing
import time
def calculate_square(number: int) -> None:
    print(f"Starting calculation for {number}", flush=True)
    # Calculate square
    result = number * number
    # Simulate a 2-second task
    time.sleep(2)
    print(f"Square of {number} = {result}", flush=True)
def main() -> None:
    start = time.perf_counter()
    processes: list[multiprocessing.Process] = []
    # Create 5 separate processes
    for number in range(1, 6):
        process = multiprocessing.Process(
            target=calculate_square,
            args=(number,)
        )
        processes.append(process)
        process.start()
    # Wait for every process to finish
    for process in processes:
        process.join()
    end = time.perf_counter()
    print(
        f"\nTotal execution time: "
        f"{end - start:.2f} seconds"
    )
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
