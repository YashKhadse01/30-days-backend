
import math
import threading
import time


class TokenRevocationList:
    """Thread-safe, in-memory JWT revocation store."""

    def __init__(self):
        self._revoked: dict[str, float] = {}
        self._lock = threading.RLock()

    def revoke(self, jti: str, expires_at: float) -> None:
        """Revoke a JWT until its expiration time."""
        if not isinstance(jti, str) or not jti:
            raise ValueError("Invalid JWT ID")

        if (
            isinstance(expires_at, bool)
            or not isinstance(expires_at, (int, float))
            or not math.isfinite(expires_at)
        ):
            raise ValueError("Invalid expiration time")

        with self._lock:
            now = time.time()
            self._cleanup(now)

            if expires_at > now:
                self._revoked[jti] = max(
                    expires_at,
                    self._revoked.get(jti, 0),
                )

    def is_revoked(self, jti: str) -> bool:
        """Check whether a JWT has been revoked."""
        if not isinstance(jti, str) or not jti:
            raise ValueError("Invalid JWT ID")

        with self._lock:
            now = time.time()
            self._cleanup(now)
            return jti in self._revoked

    def _cleanup(self, now: float) -> None:
        """Remove expired revocation entries."""
        expired = [
            jti
            for jti, expiry in self._revoked.items()
            if expiry <= now
        ]

        for jti in expired:
            del self._revoked[jti]
