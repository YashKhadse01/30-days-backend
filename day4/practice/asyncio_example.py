import asyncio
import time
async def download_file(file_name: str) -> None:
    print(f"Starting download: {file_name}")

    # Simulate an asynchronous network wait
    await asyncio.sleep(2)

    print(f"Completed download: {file_name}")
async def main() -> None:
    start = time.perf_counter()

    await asyncio.gather(
        download_file("file1.pdf"),
        download_file("file2.pdf"),
        download_file("file3.pdf"),
        download_file("file4.pdf"),
        download_file("file5.pdf"),
    )
    end = time.perf_counter()
    print(f"\nTotal execution time: {end - start:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())

#Run asyncio_example.py and observe the execution time.
#then change await asyncio.sleep(2) to await asyncio.sleep(3)

import asyncio
import time
async def download_file(file_name: str) -> None:
    print(f"Starting download: {file_name}")

    # Simulate an asynchronous network wait
    await asyncio.sleep(3)

    print(f"Completed download: {file_name}")
async def main() -> None:
    start = time.perf_counter()

    await asyncio.gather(
        download_file("file1.pdf"),
        download_file("file2.pdf"),
        download_file("file3.pdf"),
        download_file("file4.pdf"),
        download_file("file5.pdf"),
    )
    end = time.perf_counter()
    print(f"\nTotal execution time: {end - start:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
