
import hashlib
import secrets
import threading
import time
from dataclasses import dataclass
from typing import Optional


class RefreshTokenError(ValueError):
    """Raised when a refresh token is invalid or revoked."""


class RefreshTokenReuseDetected(RefreshTokenError):
    """Raised when a previously rotated token is reused."""


@dataclass
class RefreshRecord:
    token_hash: str
    user_id: str
    family_id: str
    expires_at: float
    revoked: bool = False


class RefreshTokenStore:
    """Thread-safe, in-memory refresh token rotation demo."""

    def __init__(self):
        self._tokens: dict[str, RefreshRecord] = {}
        self._revoked_families: set[str] = set()
        self._lock = threading.RLock()

    @staticmethod
    def _hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _create(
        self,
        user_id: str,
        family_id: str,
        lifetime_seconds: int,
    ) -> str:
        raw_token = secrets.token_urlsafe(48)
        token_hash = self._hash(raw_token)

        self._tokens[token_hash] = RefreshRecord(
            token_hash=token_hash,
            user_id=user_id,
            family_id=family_id,
            expires_at=time.time() + lifetime_seconds,
        )

        return raw_token

    def issue(
        self,
        user_id: str,
        lifetime_seconds: int = 604800,
    ) -> str:
        if not user_id or lifetime_seconds <= 0:
            raise ValueError("Invalid refresh token parameters")

        with self._lock:
            family_id = secrets.token_hex(16)
            return self._create(
                user_id,
                family_id,
                lifetime_seconds,
            )

    def rotate(
        self,
        token: str,
        lifetime_seconds: int = 604800,
    ) -> str:
        if not token or lifetime_seconds <= 0:
            raise RefreshTokenError("Invalid refresh token")

        token_hash = self._hash(token)

        with self._lock:
            record = self._tokens.get(token_hash)

            if record is None:
                raise RefreshTokenError("Unknown refresh token")

            if record.family_id in self._revoked_families:
                raise RefreshTokenError("Token family revoked")

            if record.revoked:
                self._revoked_families.add(record.family_id)
                raise RefreshTokenReuseDetected(
                    "Refresh token reuse detected"
                )

            if time.time() >= record.expires_at:
                record.revoked = True
                raise RefreshTokenError("Refresh token expired")

            # Revoke the old token before issuing its replacement.
            record.revoked = True

            return self._create(
                record.user_id,
                record.family_id,
                lifetime_seconds,
            )

    def is_active(self, token: str) -> bool:
        token_hash = self._hash(token)

        with self._lock:
            record = self._tokens.get(token_hash)

            return bool(
                record is not None
                and not record.revoked
                and record.family_id not in self._revoked_families
                and time.time() < record.expires_at
            )

    def revoke(self, token: str) -> None:
        token_hash = self._hash(token)

        with self._lock:
            record = self._tokens.get(token_hash)

            if record is not None:
                record.revoked = True
