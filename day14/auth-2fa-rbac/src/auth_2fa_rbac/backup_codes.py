
import hashlib
import hmac
import secrets


def hash_backup_code(code: str) -> str:
    """Hash a high-entropy recovery code."""
    normalized = code.strip().replace("-", "").upper()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def generate_backup_codes(count: int = 10) -> tuple[list[str], set[str]]:
    """Generate recovery codes and their stored hashes."""
    if count <= 0:
        raise ValueError("Count must be positive")

    codes = [
        secrets.token_hex(8).upper()
        for _ in range(count)
    ]

    hashes = {hash_backup_code(code) for code in codes}
    return codes, hashes


def redeem_backup_code(
    code: str,
    stored_hashes: set[str],
) -> bool:
    """Redeem a backup code once, removing its hash."""
    candidate = hash_backup_code(code)

    matched = None

    for stored_hash in stored_hashes:
        if hmac.compare_digest(candidate, stored_hash):
            matched = stored_hash

    if matched is None:
        return False

    stored_hashes.remove(matched)
    return True
