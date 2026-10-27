
from typing import Protocol
class Displayable(Protocol):
    def display_info(self) -> str:
        ...
class Book:
    def display_info(self) -> str:
        return "Python Programming Book"
class Magazine:
    def display_info(self) -> str:
        return "Technology Magazine"
def show_item(item: Displayable) -> None:
    print(item.display_info())
book = Book()
magazine = Magazine()
show_item(book)
show_item(magazine)

#Define an abstract LibraryItem class with display_info() and borrow().
#Create a PhysicalBook subclass that implements both methods.
#Create an EBook subclass that also implements both methods.
#Define a Displayable Protocol with display_info().
#Write show_item(item: Displayable) and call it for both book types.

from abc import ABC, abstractmethod
from typing import Protocol


class LibraryItem(ABC):

    @abstractmethod
    def display_info(self) -> str:
        pass

    @abstractmethod
    def borrow(self) -> str:
        pass


class PhysicalBook(LibraryItem):
   def __init__(self, title: str, pages: int):
           self.title = title
           self.pages = pages
   def display_info(self) -> str:
        return f"Physical Book: {self.title}, {self.pages} pages"
   def borrow(self) -> str:
        return f"{self.title} borrowed successfully"


class EBook(LibraryItem):
    def __init__(self, title: str, pages: int):
            self.title = title
            self.pages = pages
    def display_info(self) -> str:
        return f"EBook: {self.title}, {self.pages} pages"
    def borrow(self) -> str:
        return f"{self.title} borrowed successfully"


class Displayable(Protocol):
    def display_info(self) -> str:
        ...
class Book:
    def display_info(self) -> str:
        return "Django Programming Book"
class Magazine:
    def display_info(self) -> str:
        return "Technology Magazine"

def show_item(item: Displayable) -> None:
    print(item.display_info())


# Create your objects and test them here
# Create objects
physical_book = PhysicalBook("Python Basics", 250)
ebook = EBook("Learning Django", 180)

# Test both classes
show_item(physical_book)
show_item(ebook)

print(physical_book.borrow())
print(ebook.borrow())
