
import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class APIKeyRecord:
    key_id: str
    key_hash: str
    client_name: str
    scopes: set[str] = field(default_factory=set)
    revoked: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class APIKeyManager:
    """Manage hashed API keys for machine clients."""

    def __init__(self):
        self.keys: dict[str, APIKeyRecord] = {}

    @staticmethod
    def hash_key(api_key: str) -> str:
        return hashlib.sha256(
            api_key.encode("utf-8")
        ).hexdigest()

    def create_key(
        self,
        client_name: str,
        scopes: set[str],
    ) -> tuple[str, APIKeyRecord]:
        """Generate a key and store only its hash."""

        if not client_name.strip():
            raise ValueError("Client name is required")

        if not scopes:
            raise ValueError("At least one scope is required")

        key_id = secrets.token_hex(8)
        raw_key = f"ak_{secrets.token_urlsafe(32)}"

        record = APIKeyRecord(
            key_id=key_id,
            key_hash=self.hash_key(raw_key),
            client_name=client_name,
            scopes=set(scopes),
        )

        self.keys[key_id] = record

        return raw_key, record

    def authenticate(
        self,
        raw_key: str,
        required_scope: str | None = None,
    ) -> APIKeyRecord | None:
        """Authenticate a key and check its permissions."""

        candidate_hash = self.hash_key(raw_key)

        for record in self.keys.values():
            if record.revoked:
                continue

            if not secrets.compare_digest(
                candidate_hash,
                record.key_hash,
            ):
                continue

            if (
                required_scope is not None
                and required_scope not in record.scopes
            ):
                return None

            return record

        return None

    def revoke_key(self, key_id: str) -> bool:
        """Revoke a key so it can no longer authenticate."""

        record = self.keys.get(key_id)

        if record is None:
            return False

        record.revoked = True
        return True

    def rotate_key(
        self,
        key_id: str,
    ) -> tuple[str, APIKeyRecord]:
        """Replace an existing active key with a new key."""

        old_record = self.keys.get(key_id)

        if old_record is None or old_record.revoked:
            raise ValueError("Active API key not found")

        new_key, new_record = self.create_key(
            client_name=old_record.client_name,
            scopes=old_record.scopes,
        )

        old_record.revoked = True

        return new_key, new_record
