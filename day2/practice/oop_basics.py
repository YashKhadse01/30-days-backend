
'''class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author
        self.is_available = True

    def display_info(self):
        print(f"Title: {self.title}")
        print(f"Author: {self.author}")
        print(f"Available: {self.is_available}")

    def borrow_book(self):
        if self.is_available:
            self.is_available = False
            print("Book borrowed successfully!")
        else:
            print("Book is already borrowed!")


book1 = Book("Python Basics", "John Smith")

book1.display_info()
book1.borrow_book()
book1.display_info()'''


'''Create a second book named "Learning SQL".
Add a method return_book() that changes is_available back to True.
Prevent users from returning a book that is already available.
Borrow the first book twice and observe what happens.
Return the first book and display its updated information.'''


class Book2:
    def __init__(self, title, author):
        self.title = title
        self.author = author
        self.is_available = True

    def display_info(self):
        print(f"Title: {self.title}")
        print(f"Author: {self.author}")
        print(f"Available: {self.is_available}")

    def borrow_book(self):
        if self.is_available:
            self.is_available = False
            print("Book borrowed successfully!")
        else:
            print("Book is already borrowed!")

    def return_book(self):
        if not self.is_available:
            self.is_available = True
            print("Book returned successfully!")
        else:
            print("Book is already available!")


book = Book2("Learning SQL", "John Smith")

book.display_info()
book.borrow_book()
book.return_book()
book.display_info()
