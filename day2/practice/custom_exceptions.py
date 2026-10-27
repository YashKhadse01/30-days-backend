#Create first custom exceptions

class LibraryError(Exception):
    """Base exception for library-related errors."""
    pass


class BookNotFoundError(LibraryError):
    """Raised when a requested book does not exist."""
    pass


class BookAlreadyBorrowedError(LibraryError):
    """Raised when a book is already borrowed."""
    pass


class BookNotBorrowedError(LibraryError):
    """Raised when returning an available book."""
    pass
#Use custom exceptions in a Book class
class Book:
    def __init__(self, title: str):
        self.title = title
        self.is_available = True
    def borrow(self) -> None:
        if not self.is_available:
            raise BookAlreadyBorrowedError(
                f"'{self.title}' is already borrowed"
            )
        self.is_available = False
    def return_book(self) -> None:
        if self.is_available:
            raise BookNotBorrowedError(
                f"'{self.title}' was not borrowed"
            )
        self.is_available = True
book = Book("Python Basics")
try:
    book.borrow()
    print("Book borrowed successfully!")
    book.borrow()
except BookAlreadyBorrowedError as error:
    print("Error:", error)
except LibraryError as error:
    print("Library operation failed:", error)

#Create a parent exception named LibraryError.
#Create BookNotFoundError, BookAlreadyBorrowedError and BookNotBorrowedError.
#Create a Book class with title and is_available attributes.
#Implement borrow() and return_book() using custom exceptions.
#Create a dictionary of books indexed by ISBN.
#Write find_book(isbn) that raises BookNotFoundError for an unknown ISBN.
#Test successful and unsuccessful borrowing and returning with try/except.


# Step 1: Create custom exception hierarchy
class LibraryError(Exception):
    """Parent exception for library errors."""
    pass
class BookNotFoundError(LibraryError):
    pass
class BookAlreadyBorrowedError(LibraryError):
    pass
class BookNotBorrowedError(LibraryError):
    pass
# Step 2: Create Book class
class Book:
    def __init__(self, title: str):
        self.title = title
        self.is_available = True
    def borrow(self) -> None:
        if not self.is_available:
            raise BookAlreadyBorrowedError(
                f"'{self.title}' is already borrowed!"
            )
        self.is_available = False
        print(f"'{self.title}' borrowed successfully!")
    def return_book(self) -> None:
        if self.is_available:
            raise BookNotBorrowedError(
                f"'{self.title}' is not currently borrowed!"
            )
        self.is_available = True
        print(f"'{self.title}' returned successfully!") 
# Step 3: Create library collectio
books = {
    "101": Book("Python Basics"),
    "102": Book("Learning SQL"),
    "103": Book("Django Development")
}
# Step 4: Search book by ISBN
def find_book(isbn: str) -> Book:
    if isbn not in books:
        raise BookNotFoundError(
            f"Book with ISBN {isbn} was not found!"
        )

    return books[isbn]
# Step 5: Test library operations
print("--- Library Management System ---")
# Test 1: Borrow an available book
try:
    book = find_book("101")
    book.borrow()

except LibraryError as error:
    print("Error:", error)
# Test 2: Borrow the same book again
try:
    book = find_book("101")
    book.borrow()
except BookAlreadyBorrowedError as error:
    print("Error:", error)
# Test 3: Search for an invalid ISBN
try:
    book = find_book("999")
    book.borrow()
except BookNotFoundError as error:
    print("Error:", error)
# Test 4: Return a borrowed book
try:
    book = find_book("101")
    book.return_book()
except LibraryError as error:
    print("Error:", error)
# Test 5: Return the same book again
try:
    book = find_book("101")
    book.return_book()
except BookNotBorrowedError as error:
    print("Error:", error)
# Step 6: Display final availability
print("\n--- Final Book Status ---")
for isbn, book in books.items():
    print(
        f"ISBN: {isbn} | "
        f"Title: {book.title} | "
        f"Available: {book.is_available}"
    )

