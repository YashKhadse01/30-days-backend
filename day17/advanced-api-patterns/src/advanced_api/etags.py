
import hashlib
import json
from typing import Any


class ETagManager:
    """Generate and compare HTTP entity tags."""

    @staticmethod
    def generate(data: Any) -> str:
        """Generate a strong ETag from canonical JSON data."""
        serialized = json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        digest = hashlib.sha256(
            serialized.encode("utf-8")
        ).hexdigest()

        return f'"{digest}"'

    @staticmethod
    def matches(
        current_etag: str,
        provided_etag: str | None,
    ) -> bool:
        """Check exact ETag equality."""
        if provided_etag is None:
            return False

        return current_etag == provided_etag

    @staticmethod
    def is_not_modified(
        data: Any,
        if_none_match: str | None,
    ) -> bool:
        """Determine whether a cached representation is current."""
        current_etag = ETagManager.generate(data)

        return ETagManager.matches(
            current_etag,
            if_none_match,
        )

    @staticmethod
    def can_update(
        data: Any,
        if_match: str | None,
    ) -> bool:
        """Allow an update only when the resource version matches."""
        if if_match is None:
            return False

        current_etag = ETagManager.generate(data)

        return ETagManager.matches(
            current_etag,
            if_match,
        )
