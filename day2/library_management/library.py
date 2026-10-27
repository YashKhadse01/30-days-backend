
from library_management.models import Book
from library_management.interfaces import LibraryRepository
from library_management.exceptions import (
    BookNotFoundError,
    BookAlreadyExistsError,
    BookAlreadyBorrowedError,
    BookNotBorrowedError,
)


class Library(LibraryRepository):

    def __init__(self):
        self.books: dict[str, Book] = {}

    def add_book(self, book: Book) -> None:
        if book.isbn in self.books:
            raise BookAlreadyExistsError(
                f"Book with ISBN {book.isbn} already exists"
            )

        self.books[book.isbn] = book

    def find_book(self, isbn: str) -> Book:
        if isbn not in self.books:
            raise BookNotFoundError(
                f"Book with ISBN {isbn} not found"
            )

        return self.books[isbn]

    def borrow_book(self, isbn: str, borrower: str) -> None:
        book = self.find_book(isbn)

        if not book.is_available:
            raise BookAlreadyBorrowedError(
                f"'{book.title}' is already borrowed"
            )

        if not borrower.strip():
            raise ValueError("Borrower name cannot be empty")

        book.is_available = False
        book.borrowers.append(borrower)

    def return_book(self, isbn: str) -> None:
        book = self.find_book(isbn)

        if book.is_available:
            raise BookNotBorrowedError(
                f"'{book.title}' is not currently borrowed"
            )

        book.is_available = True
