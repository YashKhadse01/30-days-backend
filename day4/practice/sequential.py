import time
def download_file(file_name: str) -> None:
    print(f"Starting download: {file_name}")
    time.sleep(2)  # Simulates waiting for a download
    print(f"Completed download: {file_name}")
start = time.perf_counter()
download_file("file1.pdf")
download_file("file2.pdf")
download_file("file3.pdf")
end = time.perf_counter()
print(f"\nTotal execution time: {end - start:.2f} seconds")

#Suppose three users request files from your API.
#With sequential execution, each task waits for the previous task to finish. But with concurrency, we can overlap waiting periods and potentially reduce total processing time.

import time
def download_file(file_name: str) -> None:
    print(f"Starting download: {file_name}")
    # Simulate a 2-second download
    time.sleep(2)
    print(f"Completed download: {file_name}")
def main() -> None:
    start = time.perf_counter()
    download_file("file1.pdf")
    download_file("file2.pdf")
    download_file("file3.pdf")
    end = time.perf_counter()
    print(f"\nTotal execution time: {end - start:.2f} seconds")
if __name__ == "__main__":
    main()
