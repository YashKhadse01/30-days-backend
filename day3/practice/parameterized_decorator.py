#decorators that accept their own arguments.
from functools import wraps

def repeat(times):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            for i in range(times):
                func(*args, **kwargs)

        return wrapper

    return decorator


@repeat(times=3)
def greet(name):
    print(f"Hello, {name}!")


greet("Buddy")