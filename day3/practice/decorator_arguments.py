from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Function execution started")

        result = func(*args, **kwargs)

        print("Function execution completed")

        return result

    return wrapper


@my_decorator
def add(a, b):
    return a + b


answer = add(10, 20)
print("Result:", answer)

#Modify the example to decorate this function.

from functools import wraps

def my_decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        print("Function execution started")

        result = func(*args, **kwargs)

        print("Function execution completed")

        return result

    return wrapper


@my_decorator
def calculate_salary(basic, bonus=0):
    return basic + bonus


salary = calculate_salary(30000, bonus=5000)

print("Total Salary:", salary)

