#Example using a built-in iterator
numbers = [10, 20, 30]
iterator = iter(numbers)
print(next(iterator))
print(next(iterator))
print(next(iterator))

#Build your own iterator class
class NumberIterator:
    def __init__(self, limit):
        self.limit = limit
        self.current = 1
    def __iter__(self):
        return self
    def __next__(self):
        if self.current > self.limit:
            raise StopIteration
        number = self.current
        self.current += 1
        return number
numbers = NumberIterator(5)
for number in numbers:
    print(number)

#Create a custom iterator called EvenNumberIterator
class EvenNumberIterator:
    def __init__(self, limit):
        self.limit = limit
        self.current = 2
    def __iter__(self):
        return self
    def __next__(self):
        if self.current > self.limit:
            raise StopIteration
        number = self.current
        self.current += 2
        return number
# Create iterator object
numbers = EvenNumberIterator(10)
# Print even numbers
for number in numbers:
    print(number)
#Using next() manually
numbers = EvenNumberIterator(6)
print(next(numbers))  # 2
print(next(numbers))  # 4
print(next(numbers))  # 6
