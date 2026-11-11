
import hashlib
import json
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class IdempotencyRecord:
    request_hash: str
    response: dict[str, Any]
    status_code: int
    expires_at: float


class IdempotencyConflict(Exception):
    """Key was reused with a different request."""


class IdempotencyManager:
    """In-memory idempotency manager for API demonstrations."""

    def __init__(self, ttl_seconds: int = 3600):
        if ttl_seconds <= 0:
            raise ValueError("TTL must be positive")

        self.ttl_seconds = ttl_seconds
        self.records: dict[str, IdempotencyRecord] = {}
        self._lock = threading.Lock()

    @staticmethod
    def hash_request(payload: dict[str, Any]) -> str:
        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

    def execute(
        self,
        key: str,
        payload: dict[str, Any],
        operation: Callable[[], dict[str, Any]],
        *,
        status_code: int = 201,
        namespace: str = "default",
    ) -> tuple[dict[str, Any], int, bool]:
        """
        Execute once per namespace/key combination.

        Returns:
            response, status_code, was_replayed
        """

        if not key or not key.strip():
            raise ValueError("Idempotency key is required")

        if not namespace or not namespace.strip():
            raise ValueError("Namespace is required")

        request_hash = self.hash_request(payload)
        storage_key = f"{namespace}:{key}"

        with self._lock:
            now = time.time()
            existing = self.records.get(storage_key)

            if existing and existing.expires_at > now:
                if existing.request_hash != request_hash:
                    raise IdempotencyConflict(
                        "Idempotency key reused with different payload"
                    )

                return (
                    existing.response.copy(),
                    existing.status_code,
                    True,
                )

            if existing:
                del self.records[storage_key]

            response = operation()

            self.records[storage_key] = IdempotencyRecord(
                request_hash=request_hash,
                response=response.copy(),
                status_code=status_code,
                expires_at=time.time() + self.ttl_seconds,
            )

            return response.copy(), status_code, False
