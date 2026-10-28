import time
import pytest
from decorators import cache, retry, timed
# TEST 1: Timed decorator returns correct result
def test_timed_result() -> None:
    @timed
    def add(a: int, b: int) -> int:
        return a + b
    assert add(10, 20) == 30
# TEST 2: Timed decorator preserves function name
def test_timed_function_name() -> None:
    @timed
    def greet() -> str:
        return "Hello"
    assert greet.__name__ == "greet"
# TEST 3: Timed decorator prints execution time
def test_timed_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    @timed
    def task() -> int:
        return 42
    assert task() == 42
    output = capsys.readouterr().out
    assert "task executed in" in output
# TEST 4: Retry succeeds after temporary failures
def test_retry_success() -> None:
    attempts = 0
    @retry(max_attempts=3)
    def connect() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError("Temporary failure")
        return "Connected"
    assert connect() == "Connected"
    assert attempts == 3
# TEST 5: Retry raises error after final attempt
def test_retry_failure() -> None:
    attempts = 0
    @retry(max_attempts=2)
    def connect() -> None:
        nonlocal attempts
        attempts += 1
        raise ConnectionError("Unavailable")
    with pytest.raises(ConnectionError):
        connect()
    assert attempts == 2
# TEST 6: Retry rejects invalid attempts
def test_retry_invalid_attempts() -> None:
    with pytest.raises(ValueError):
        retry(max_attempts=0)
# TEST 7: Cache stores repeated results
def test_cache_hit() -> None:
    calls = 0
    @cache(ttl=5)
    def square(number: int) -> int:
        nonlocal calls
        calls += 1
        return number * number
    assert square(10) == 100
    assert square(10) == 100
    assert calls == 1
# TEST 8: Cache expires after TTL
def test_cache_expiration() -> None:
    calls = 0
    @cache(ttl=0.05)
    def square(number: int) -> int:
        nonlocal calls
        calls += 1
        return number * number
    assert square(5) == 25
    time.sleep(0.1)
    assert square(5) == 25
    assert calls == 2
# TEST 9: Cache uses different argument keys
def test_cache_different_arguments() -> None:
    calls = 0
    @cache(ttl=5)
    def square(number: int) -> int:
        nonlocal calls
        calls += 1
        return number * number
    assert square(2) == 4
    assert square(3) == 9
    assert calls == 2
# TEST 10: Cache rejects invalid TTL
def test_cache_invalid_ttl() -> None:
    with pytest.raises(ValueError):
        cache(ttl=0)
