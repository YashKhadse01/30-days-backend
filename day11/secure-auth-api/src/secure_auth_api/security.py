import hashlib
import hmac
import secrets

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SALT_BYTES = 16

def hash_password(password: str) -> str:
    """Hash a password using scrypt and a unique random salt."""
    salt = secrets.token_bytes(SALT_BYTES)

    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=32,
    )

    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${password_hash.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against its stored scrypt hash."""
    try:
        algorithm, n, r, p, salt_hex, expected_hex = stored_hash.split("$")

        if algorithm != "scrypt":
            return False

        n, r, p = int(n), int(r), int(p)

        # Only accept the supported work parameters.
        if (n, r, p) != (SCRYPT_N, SCRYPT_R, SCRYPT_P):
            return False

        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(expected_hex)

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