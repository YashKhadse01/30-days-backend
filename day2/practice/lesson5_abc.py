#Imagine our library contains two types of books: physical books and e-books.
#Both must support a display_info() method and a borrow() method, but their implementations can differ.
#An ABC defines that requirement.

from abc import ABC, abstractmethod
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
book = PhysicalBook("Python Basics", 250)

print(book.display_info())
print(book.borrow())

#Why do we use @abstractmethod?
#If you create a subclass without implementing borrow():
'''class EBook(LibraryItem):
    def display_info(self) -> str:
        return "E-book information"


ebook = EBook()''' 
#Python raises a TypeError, because EBook hasn't implemented all the required abstract methods.
#That helps prevent incomplete subclasses from being instantiated.