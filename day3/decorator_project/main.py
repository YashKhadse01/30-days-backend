import time
from decorators import timed
@timed
def process_data(count: int) -> int:
    time.sleep(1)
    return sum(range(count))
@timed
def calculate_salary(
    basic_salary: int,
    bonus: int
) -> int:
    return basic_salary + bonus
print("Processing data...")
result = process_data(1000)
print("Result:", result)
print("\nCalculating salary...")
salary = calculate_salary(30000, 5000)
print("Total salary:", salary)
from decorators import retry
attempt_counter = 0
@retry(max_attempts=3)
def connect_to_server() -> str:
    global attempt_counter
    attempt_counter += 1
    if attempt_counter < 3:
        raise ConnectionError("Server unavailable")
    return "Connected successfully!"
print("\nConnecting to server...")
print(connect_to_server())

from decorators import cache
@cache(ttl=3)
def calculate_square(number: int) -> int:
    print("Calculating square...")
    return number * number
print("\nFirst call:")
print(calculate_square(10))
print("\nSecond call:")
print(calculate_square(10))
print("\nWaiting for cache to expire...")
time.sleep(4)
print("\nThird call:")
print(calculate_square(10))
