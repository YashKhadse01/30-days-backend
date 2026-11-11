
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from advanced_api.idempotency import (
    IdempotencyConflict,
    IdempotencyManager,
)


@pytest.fixture
def manager():
    return IdempotencyManager(ttl_seconds=60)


def test_first_request_executes(manager):
    calls = []

    def operation():
        calls.append("executed")
        return {"order_id": 101}

    response, status, replayed = manager.execute(
        "key-001",
        {"product": "Laptop"},
        operation,
    )

    assert response == {"order_id": 101}
    assert status == 201
    assert replayed is False
    assert len(calls) == 1


def test_same_key_returns_cached_response(manager):
    calls = []

    def operation():
        calls.append("executed")
        return {"order_id": 102}

    first = manager.execute(
        "key-002",
        {"product": "Keyboard"},
        operation,
    )

    second = manager.execute(
        "key-002",
        {"product": "Keyboard"},
        operation,
    )

    assert first[0] == second[0]
    assert second[2] is True
    assert len(calls) == 1


def test_different_payload_raises_conflict(manager):
    manager.execute(
        "key-003",
        {"amount": 100},
        lambda: {"payment_id": 1},
    )

    with pytest.raises(IdempotencyConflict):
        manager.execute(
            "key-003",
            {"amount": 200},
            lambda: {"payment_id": 2},
        )


def test_different_keys_execute_separately(manager):
    calls = []

    def operation():
        calls.append(1)
        return {"success": True}

    manager.execute("key-A", {"x": 1}, operation)
    manager.execute("key-B", {"x": 1}, operation)

    assert len(calls) == 2


def test_different_namespaces_are_independent(manager):
    calls = []

    def operation():
        calls.append(1)
        return {"success": True}

    manager.execute(
        "shared-key",
        {"x": 1},
        operation,
        namespace="client-A",
    )

    manager.execute(
        "shared-key",
        {"x": 1},
        operation,
        namespace="client-B",
    )

    assert len(calls) == 2


def test_expired_key_allows_new_execution(manager):
    calls = []

    def operation():
        calls.append(1)
        return {"count": len(calls)}

    manager.execute(
        "expiring-key",
        {"x": 1},
        operation,
    )

    manager.records["default:expiring-key"].expires_at = (
        time.time() - 1
    )

    response, _, replayed = manager.execute(
        "expiring-key",
        {"x": 1},
        operation,
    )

    assert replayed is False
    assert response["count"] == 2
    assert len(calls) == 2


def test_invalid_ttl_rejected():
    with pytest.raises(ValueError):
        IdempotencyManager(ttl_seconds=0)


def test_empty_key_rejected(manager):
    with pytest.raises(ValueError):
        manager.execute(
            "",
            {"x": 1},
            lambda: {"ok": True},
        )


def test_empty_namespace_rejected(manager):
    with pytest.raises(ValueError):
        manager.execute(
            "key",
            {"x": 1},
            lambda: {"ok": True},
            namespace="",
        )


def test_payload_order_does_not_change_hash(manager):
    first_hash = manager.hash_request(
        {"name": "Laptop", "price": 500}
    )

    second_hash = manager.hash_request(
        {"price": 500, "name": "Laptop"}
    )

    assert first_hash == second_hash


def test_concurrent_requests_execute_once(manager):
    execution_count = 0
    counter_lock = threading.Lock()
    barrier = threading.Barrier(5)

    def operation():
        nonlocal execution_count

        with counter_lock:
            execution_count += 1

        time.sleep(0.02)

        return {"order_id": 999}

    def worker():
        barrier.wait()

        return manager.execute(
            "concurrent-key",
            {"product": "Mouse"},
            operation,
        )

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(
            lambda _: worker(),
            range(5),
        ))

    assert execution_count == 1
    assert all(
        result[0] == {"order_id": 999}
        for result in results
    )

    assert sum(
        result[2] is False
        for result in results
    ) == 1

    assert sum(
        result[2] is True
        for result in results
    ) == 4


def test_custom_status_code_preserved(manager):
    first = manager.execute(
        "status-key",
        {"x": 1},
        lambda: {"accepted": True},
        status_code=202,
    )

    second = manager.execute(
        "status-key",
        {"x": 1},
        lambda: {"accepted": False},
        status_code=201,
    )

    assert first[1] == 202
    assert second[1] == 202
    assert second[2] is True
