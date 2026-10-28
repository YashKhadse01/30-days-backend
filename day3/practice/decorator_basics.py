#Understand functions inside functions
def outer():
    print("Outer function started")

    def inner():
        print("Inner function executed")

    inner()

outer()

#Return a function instead of calling it
def outer():
    def inner():
        print("Hello from inner function")

    return inner

my_function = outer()
my_function()

#Create your first decorator
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper():
        print("Before function execution")
        func()
        print("After function execution")

    return wrapper


@my_decorator
def greet():
    print("Hello, buddy!")


greet()

#Write a decorator named welcome_decorator that produces this output when study() is called:

from functools import wraps

def welcome_decorator(func):
    @wraps(func)
    def wrapper():
        print("Welcome to Day 3")
        func()
        print("Day 3 session completed")

    return wrapper


@welcome_decorator
def study():
    print("Learning Advanced Python")


study()