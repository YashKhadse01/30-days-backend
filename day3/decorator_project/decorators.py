import time
from functools import wraps
from typing import Callable, ParamSpec, TypeVar, cast
P = ParamSpec("P")
R = TypeVar("R")
# 1. TIMED DECORATOR

def timed(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(
        *args: P.args,
        **kwargs: P.kwargs
    ) -> R:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            end = time.perf_counter()
            print(
                f"{func.__name__} executed in "
                f"{end - start:.4f} seconds"
            )
    return wrapper
# 2. RETRY DECORATOR
def retry(
    max_attempts: int = 3,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if max_attempts < 1:
        raise ValueError(
            "max_attempts must be at least 1"
        )
    def decorator(
        func: Callable[P, R]
    ) -> Callable[P, R]:
        @wraps(func)
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs
        ) -> R:
            # Retry all attempts except the last
            for attempt in range(1, max_attempts):
                try:
                    return func(*args, **kwargs)
                except ConnectionError:
                    print(f"Attempt {attempt} failed")
            # Final attempt: let any error propagate
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 3. CACHE DECORATOR WITH TTL
def cache(
    ttl: float = 5.0,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if ttl <= 0:
        raise ValueError(
            "ttl must be greater than zero"
        )
    def decorator(
        func: Callable[P, R]
    ) -> Callable[P, R]:
        stored: dict[
            object,
            tuple[object, float]
        ] = {}
        @wraps(func)
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs
        ) -> R:
            key = (
                args,
                frozenset(kwargs.items())
            )
            now = time.monotonic()
            if key in stored:
                result, expires_at = stored[key]
                if now < expires_at:
                    print("Cache HIT")
                    return cast(R, result)
            print("Cache MISS")
            result = func(*args, **kwargs)
            stored[key] = (
                result,
                time.monotonic() + ttl
            )
            return result
        return wrapper
    return decorator
