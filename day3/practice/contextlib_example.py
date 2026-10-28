#@contextmanager, which lets us build context managers using generators.
from contextlib import contextmanager
@contextmanager
def file_manager(filename):
    print("Opening file...")
    file = open(filename, "w")
    try:
        yield file
    finally:
        file.close()
        print("File closed successfully")
with file_manager("day3_notes.txt") as file:
    file.write("Learning contextlib!")
    print("Writing data to file...")
