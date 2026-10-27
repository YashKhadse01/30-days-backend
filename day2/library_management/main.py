
from library_management.models import Book
from library_management.library import Library
from library_management.exceptions import LibraryError


def main():
    library = Library()

    book1 = Book("Python Basics", "John", "101", 250, 499.0)
    book2 = Book("Django", "David", "102", 300, 599.0)

    library.add_book(book1)
    library.add_book(book2)

    try:
        library.borrow_book("101", "Rahul")
        print("Book borrowed successfully!")

        library.return_book("101")
        print("Book returned successfully!")

        print("Book details:", library.find_book("101"))

    except LibraryError as error:
        print("Library error:", error)


if __name__ == "__main__":
    main()
