
class Book:
    def __init__(self, title, pages, price):
        self.title = title
        self.pages = pages
        self.price = price

    @property
    def pages(self):
        return self._pages

    @pages.setter
    def pages(self, value):
        if type(value) is not int or value <= 0:
            raise ValueError("Pages must be a positive integer")

        self._pages = value
    @property
    def price(self):
        return self._price
    @price.setter
    def price(self, value):
        if type(value) is not int or value <=0:
            raise ValueError("Price must be positive integer")
        self._price = value


book1 = Book("Python Basics", 250,1000)

print(book1.title)
print(book1.pages)
print(book1.price)

book1.pages = 100
print("Updated pages:", book1.pages)
book1.price = 1000
print("Updated price:",book1.price )

'''@price.setter
def price(self, value):
    # Check whether value is a valid number
    # Reject values below zero
    # Store the valid price in self._price'''