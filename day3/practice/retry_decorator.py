#Building a Real @retry Decorator
from functools import wraps


def retry(max_attempts=3):

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            for attempt in range(1, max_attempts + 1):

                try:
                    print(f"Attempt {attempt}")

                    result = func(*args, **kwargs)

                    return result

                except ConnectionError:

                    if attempt == max_attempts:
                        print("All retry attempts failed")
                        raise

                    print("Connection failed. Retrying...")

        return wrapper

    return decorator


counter = 0


@retry(max_attempts=3)
def fetch_data():

    global counter
    counter += 1

    if counter < 3:
        raise ConnectionError("Server unavailable")

    return "Data fetched successfully!"


print(fetch_data())

#Retry Decorator, with max_attempts=2

from functools import wraps


def retry(max_attempts=2):

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            for attempt in range(1, max_attempts + 1):

                try:
                    print(f"Attempt {attempt}")

                    result = func(*args, **kwargs)

                    return result

                except ConnectionError:

                    if attempt == max_attempts:
                        print("All retry attempts failed")
                        raise

                    print("Connection failed. Retrying...")

        return wrapper

    return decorator


counter = 0


@retry(max_attempts=2)
def fetch_data():

    global counter
    counter += 1

    if counter < 3:
        raise ConnectionError("Server unavailable")

    return "Data fetched successfully!"


try:
    print(fetch_data())

except ConnectionError as error:
    print(f"Final error: {error}")