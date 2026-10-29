import time
import threading
def download_file(file_name: str) -> None:
    print(f"Starting download: {file_name}")
    time.sleep(2)
    print(f"Completed download: {file_name}")
def main() -> None:
    start = time.perf_counter()
    threads: list[threading.Thread] = []
    for i in range(1, 4):
        thread = threading.Thread(
            target=download_file,
            args=(f"file{i}.pdf",)
        )
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    end = time.perf_counter()
    print(f"\nTotal execution time: {end - start:.2f} seconds")
if __name__ == "__main__":
    main()

#Run threading_example.py and compare its execution time with sequential.py.
#Then change the number of files from 3 to 5:

import time
import threading
def download_file(file_name: str) -> None:
    print(f"Starting download: {file_name}")
    # Simulate downloading a file for 2 seconds
    time.sleep(2)
    print(f"Completed download: {file_name}")
def main() -> None:
    start = time.perf_counter()
    threads: list[threading.Thread] = []
    # Create and start 5 threads
    for i in range(1, 6):
        thread = threading.Thread(
            target=download_file,
            args=(f"file{i}.pdf",)
        )
        threads.append(thread)
        thread.start()
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    end = time.perf_counter()
    print(f"\nTotal execution time: {end - start:.2f} seconds")
if __name__ == "__main__":
    main()
