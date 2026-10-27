
from dataclasses import dataclass

@dataclass
class Book:
    title: str
    author: str
    isbn: str
    pages: int
    price: float


book1 = Book("Python Basics", "John Smith", "101", 250, 499.0)
book2 = Book("Python Basics", "John Smith", "101", 250, 499.0)
book3 = Book("Learning SQL", "David", "102", 300, 599.0)

print(book1)
print(book1.title)
print(book1 == book2)
print(book1 == book3)

# What happens if someone creates a book with negative pages?

from dataclasses import dataclass

@dataclass
class Book:
    title: str
    author: str
    isbn: str
    pages: int
    price: float

    def __post_init__(self):
        if type(self.pages) is not int or self.pages <= 0:
            raise ValueError("Pages must be a positive integer")

        if type(self.price) not in (int, float) or self.price < 0:
            raise ValueError("Price must be non-negative")


book1 = Book("Python Basics", "John Smith", "101", 250, 499.0)
print(book1)

try:
    book2 = Book("Learning SQL", "David", "102", -20, 599.0)
except ValueError as error:
    print("Error:", error)

#Suppose every book has a list of borrowers.
#We should not give every book the same shared list.
#Instead, use field(default_factory=list)
from dataclasses import dataclass, field

@dataclass
class Book:
    title: str
    borrowers: list[str] = field(default_factory=list)


book1 = Book("Python Basics")
book2 = Book("Learning SQL")

book1.borrowers.append("Rahul")

print(book1.borrowers)  # ['Rahul']
print(book2.borrowers)  # []

#Create a Book dataclass with title, author, isbn, pages and price.
#Add is_available with default value True.
#Add borrowers using field(default_factory=list).
# Use __post_init__() to reject invalid page counts and negative prices.
# Create a borrow_book(name) method that records the borrower and sets is_available to False.
# Create two books and demonstrate that their borrowers lists are independent.

from dataclasses import dataclass, field


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    pages: int
    price: float

    is_available: bool = True
    borrowers: list[str] = field(default_factory=list)

    def __post_init__(self):
        if type(self.pages) is not int or self.pages <= 0:
            raise ValueError("Pages must be a positive integer")

        if type(self.price) not in (int, float) or self.price < 0:
            raise ValueError("Price must be a non-negative number")

    def borrow_book(self, name):
        if self.is_available:
            self.is_available = False
            self.borrowers.append(name)
            print(f"{name} borrowed '{self.title}' successfully!")
        else:
            print(f"'{self.title}' is already borrowed!")

    def return_book(self):
        if not self.is_available:
            self.is_available = True
            print(f"'{self.title}' returned successfully!")
        else:
            print(f"'{self.title}' is already available!")


# Create two book objects
book1 = Book("Python Basics", "John Smith", "101", 250, 499.0)
book2 = Book("Learning SQL", "David", "102", 300, 599.0)
book3 = Book("Django","Yash","103",400,699)

# Borrow the first book
book1.borrow_book("Rahul")
book3.borrow_book("Yash")
# Try borrowing the same book again
book1.borrow_book("Amit")

# Borrow the second book
book2.borrow_book("Amit")

# Display borrower histories
print("\n--- Borrower History ---")
print("Book 1:", book1.borrowers)
print("Book 2:", book2.borrowers)
print("Book 3:",book3.borrowers)

# Return the first book
book1.return_book()
book3.return_book()

# Borrow it again
book1.borrow_book("Amit")

# Display updated status
print("\n--- Final Status ---")
print("Book 1 available:", book1.is_available)
print("Book 2 available:", book2.is_available)
print("Book 3 available", book3.is_available)
print("Book 1 history:", book1.borrowers)
print("Book 2 history:", book2.borrowers)
print("Book 3 history:", book3.borrowers)
