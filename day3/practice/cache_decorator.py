#TTL Cache Decorator
import time
from functools import wraps
def cache(ttl=5):
    if ttl <= 0:
        raise ValueError("TTL must be positive")
    def decorator(func):
        stored_results = {}
        @wraps(func)
        def wrapper(*args):
            now = time.monotonic()
            if args in stored_results:
                result, expiry = stored_results[args]
                if now < expiry:
                    print("Cache HIT")
                    return result
            print("Cache MISS")
            result = func(*args)

            stored_results[args] = (
                result,
                time.monotonic() + ttl
            )
            return result
        return wrapper
    return decorator
@cache(ttl=5)
def calculate_square(number):
    print("Calculating...")
    return number * number
print("First call:", calculate_square(10))
print("Second call:", calculate_square(10))
print("Waiting for cache to expire...")
time.sleep(6)
print("Third call:", calculate_square(10))

#chnage chache ttl=5 to chache ttl=3 and change time.sleep=6 to time.sleep=4
#TTL Cache Decorator, with ttl=3 and time.sleep(4)

import time
from functools import wraps
# Step 1: Create a TTL cache decorator
def cache(ttl=3):
    if ttl <= 0:
        raise ValueError("TTL must be positive")
    def decorator(func):
        stored_results = {}
        @wraps(func)
        def wrapper(*args):
            now = time.monotonic()
            # Step 2: Check if the result is cached
            if args in stored_results:
                result, expiry = stored_results[args]
                if now < expiry:
                    print("Cache HIT")
                    return result
            # Step 3: Calculate if cache is missing or expired
            print("Cache MISS")
            result = func(*args)
            # Step 4: Store result with expiration time
            stored_results[args] = (
                result,
                time.monotonic() + ttl
            )
            return result
        return wrapper
    return decorator
# Step 5: Apply decorator
@cache(ttl=3)
def calculate_square(number):
    print("Calculating...")
    return number * number
# Step 6: Test caching
print("First call:", calculate_square(10))
print("Second call:", calculate_square(10))
print("Waiting for cache to expire...")
time.sleep(4)
print("Third call:", calculate_square(10))