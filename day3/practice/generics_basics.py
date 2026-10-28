#Python Generics and TypeVar
from typing import TypeVar
T = TypeVar("T")
def get_first(items: list[T]) -> T:
    if not items:
        raise ValueError("List cannot be empty")
    return items[0]
numbers = [10, 20, 30]
names = ["Rahul", "Amit", "Yash"]
first_number = get_first(numbers)
first_name = get_first(names)
print("First number:", first_number)
print("First name:", first_name)

#create a generic function called get_last() that works with integers, strings, and other data types.
from typing import TypeVar
# Step 1: Create a generic type variable
T = TypeVar("T")
# Step 2: Create a generic function
def get_last(items: list[T]) -> T:
    if not items:
        raise ValueError("List cannot be empty")
    return items[-1]
# Step 3: Test with integers
numbers = [10, 20, 30]
print("Last number:", get_last(numbers))
# Step 4: Test with strings
technologies = ["Python", "Django", "FastAPI"]
print("Last technology:", get_last(technologies))
# Step 5: Test with floating-point numbers
prices = [99.5, 199.5, 299.5]
print("Last price:", get_last(prices))
try:
    print(get_last([]))
except ValueError as error:
    print("Error:", error)