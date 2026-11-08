
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    if not isinstance(password, str) or not password:
        raise ValueError("Password cannot be empty")

    return password_hasher.hash(password)


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:
    """Verify a password against its stored hash."""
    if not isinstance(password, str):
        return False

    if not isinstance(stored_hash, str):
        return False

    try:
        return password_hasher.verify(
            stored_hash,
            password,
        )
    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ):
        return False


def needs_password_rehash(stored_hash: str) -> bool:
    """Check whether a password hash needs upgrading."""
    return password_hasher.check_needs_rehash(stored_hash)
