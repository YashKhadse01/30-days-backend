
import pytest

from library_management.models import Book
from library_management.library import Library
from library_management.exceptions import (
    BookNotFoundError,
    BookAlreadyExistsError,
    BookAlreadyBorrowedError,
    BookNotBorrowedError,
)


@pytest.fixture
def library():
    lib = Library()
    lib.add_book(Book("Python Basics", "John", "101", 250, 499.0))
    return lib


def test_add_book(library):
    book = Book("Django", "David", "102", 300, 599.0)
    library.add_book(book)

    assert library.find_book("102") is book


def test_duplicate_book(library):
    book = Book("Duplicate", "John", "101", 200, 300.0)

    with pytest.raises(BookAlreadyExistsError):
        library.add_book(book)


def test_find_existing_book(library):
    book = library.find_book("101")

    assert book.title == "Python Basics"


def test_book_not_found(library):
    with pytest.raises(BookNotFoundError):
        library.find_book("999")


def test_borrow_book(library):
    library.borrow_book("101", "Rahul")

    book = library.find_book("101")
    assert book.is_available is False
    assert book.borrowers == ["Rahul"]


def test_borrow_already_borrowed_book(library):
    library.borrow_book("101", "Rahul")

    with pytest.raises(BookAlreadyBorrowedError):
        library.borrow_book("101", "Amit")


def test_empty_borrower_name(library):
    with pytest.raises(ValueError):
        library.borrow_book("101", "   ")


def test_return_book(library):
    library.borrow_book("101", "Rahul")
    library.return_book("101")

    assert library.find_book("101").is_available is True


def test_return_available_book(library):
    with pytest.raises(BookNotBorrowedError):
        library.return_book("101")


def test_borrow_missing_book(library):
    with pytest.raises(BookNotFoundError):
        library.borrow_book("999", "Rahul")


def test_return_missing_book(library):
    with pytest.raises(BookNotFoundError):
        library.return_book("999")

from library_management.interfaces import LibraryRepository


def test_abstract_repository_cannot_be_instantiated():
    with pytest.raises(TypeError):
        LibraryRepository()


def test_repository_is_abstract():
    assert LibraryRepository.__abstractmethods__ == {
        "add_book",
        "find_book",
    }

from library_management.main import main


def test_main_success(capsys):
    main()

    output = capsys.readouterr().out

    assert "Book borrowed successfully!" in output
    assert "Book returned successfully!" in output
    assert "Python Basics by John" in output

def test_abstract_add_book_body():
    repository = object.__new__(LibraryRepository)

    with pytest.raises(NotImplementedError):
        LibraryRepository.add_book(repository, None)


def test_abstract_find_book_body():
    repository = object.__new__(LibraryRepository)

    with pytest.raises(NotImplementedError):
        LibraryRepository.find_book(repository, "101")

def test_abstract_add_book_body():
    with pytest.raises(NotImplementedError):
        LibraryRepository.add_book(None, None)


def test_abstract_find_book_body():
    with pytest.raises(NotImplementedError):
        LibraryRepository.find_book(None, "101")

import runpy
from unittest.mock import patch

from library_management.main import main
from library_management.exceptions import LibraryError



def test_main_handles_library_error(capsys):
    with patch(
        "library_management.main.Library.borrow_book",
        side_effect=LibraryError("Test failure")
    ):
        main()

    output = capsys.readouterr().out

    assert "Library error: Test failure" in output


def test_main_entry_point(capsys):
    runpy.run_module(
        "library_management.main",
        run_name="__main__"
    )

    output = capsys.readouterr().out

    assert "Book borrowed successfully!" in output
    assert "Book returned successfully!" in output
