#Build a custom context manager
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    def __enter__(self):
        print("Opening file...")
        self.file = open(self.filename, self.mode)
        return self.file
    def __exit__(self, exc_type, exc_value, traceback):
        if self.file is not None:
            self.file.close()
        print("File closed successfully")
with FileManager("notes.txt", "w") as file:
    file.write("Welcome to Day 3!")
    print("Writing data to file...")

