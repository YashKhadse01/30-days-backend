
import pytest
from library_management.models import Book


def test_book_creation():
    book = Book("Python Basics", "John", "101", 250, 499.0)
    assert book.title == "Python Basics"
    assert book.is_available is True
    assert book.price == 499.0


def test_book_length():
    book = Book("Python", "John", "102", 200, 300.0)
    assert len(book) == 200


def test_book_equality():
    book1 = Book("Python", "John", "101", 200, 300.0)
    book2 = Book("Django", "David", "101", 350, 500.0)
    assert book1 == book2


def test_invalid_pages():
    with pytest.raises(ValueError):
        Book("Python", "John", "103", -10, 300.0)


def test_negative_price():
    with pytest.raises(ValueError):
        Book("Python", "John", "104", 200, -100.0)


def test_price_setter():
    book = Book("Python", "John", "105", 200, 300.0)
    book.price = 450.0
    assert book.price == 450.0


def test_empty_title():
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Book("", "John", "106", 200, 300.0)


def test_empty_isbn():
    with pytest.raises(ValueError, match="ISBN cannot be empty"):
        Book("Python", "John", "", 200, 300.0)


def test_invalid_price_update():
    book = Book("Python", "John", "107", 200, 300.0)
    with pytest.raises(ValueError):
        book.price = -50


def test_book_inequality_with_other_type():
    book = Book("Python", "John", "108", 200, 300.0)
    assert book != "Python"


def test_book_hash():
    book = Book("Python", "John", "109", 200, 300.0)
    assert hash(book) == hash("109")
