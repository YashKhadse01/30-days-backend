
class Book:
    def __init__(self, title, author, isbn,pages):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.pages = pages

    def __str__(self):
        return f"{self.title} by {self.author}"

    def __repr__(self):
        return (
            f"Book(title={self.title!r}, "
            f"author={self.author!r}, isbn={self.isbn!r})"
            f"pages={self.pages!r}"
        )

    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return self.isbn == other.isbn
    def __len__(self):
        return(self.pages)


book1 = Book("Python Basics", "John Smith", "101",86)
book2 = Book("Python Basics", "John Smith", "101",99)
book3 = Book("Learning SQL", "David", "102",5)

print(book1)
print(repr(book1))
print(len(book1))
print(book1 == book2)
print(book1 == book3)


'''Add a pages attribute to the constructor.
Implement __len__() so len(book1) returns the number of pages.
Create two books with different ISBNs but identical titles.
Compare them using == and print the result.'''