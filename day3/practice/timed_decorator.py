#Build our @timed decorator
import time
from functools import wraps


def timed(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        start = time.perf_counter()

        try:
            return func(*args, **kwargs)

        finally:
            end = time.perf_counter()

            execution_time = end - start

            print(
                f"{func.__name__} executed in "
                f"{execution_time:.4f} seconds"
            )

    return wrapper


@timed
def fetch_data():
    time.sleep(2)
    return "Data fetched successfully!"


result = fetch_data()
print(result)

#Use the same @timed decorator on a function called calculate_sum().
#It should calculate the sum of numbers from 1 to 1,000,000.
import time
from functools import wraps


# Step 1: Create timed decorator
def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end = time.perf_counter()
            execution_time = end - start
            print(
                f"{func.__name__} executed in "
                f"{execution_time:.4f} seconds"
            )
    return wrapper
# Step 2: First function
@timed
def fetch_data():
    time.sleep(2)
    return "Data fetched successfully!"
# Step 3: Second function
@timed
def calculate_sum():
    total = sum(range(1, 1_000_001))
    return total
# Step 4: Execute both functions
print(fetch_data())

print("Sum:", calculate_sum())