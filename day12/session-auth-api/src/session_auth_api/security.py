
import hashlib
import hmac
import secrets

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Hash a password using scrypt and a random salt."""
    salt = secrets.token_bytes(SALT_BYTES)

    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=32,
    )

    return (
        f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}"
        f"${salt.hex()}${digest.hex()}"
    )


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password without exposing the stored hash."""
    try:
        algorithm, n, r, p, salt_hex, digest_hex = (
            stored_hash.split("$")
        )

        if algorithm != "scrypt":
            return False

        n, r, p = int(n), int(r), int(p)

        if (n, r, p) != (SCRYPT_N, SCRYPT_R, SCRYPT_P):
            return False

        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)

        if len(salt) != SALT_BYTES or len(expected) != 32:
            return False

        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=32,
        )

        return hmac.compare_digest(actual, expected)

    except (ValueError, TypeError):
        return False
