import base64
import hashlib
import hmac
import time

import pyotp
from cryptography.fernet import Fernet, InvalidToken


def derive_encryption_key(master_key: str) -> bytes:
    """Derive a Fernet-compatible key from dedicated key material."""
    if len(master_key.encode("utf-8")) < 32:
        raise ValueError("Encryption key must contain at least 32 bytes")

    digest = hashlib.sha256(master_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def encrypt_totp_secret(secret: str, master_key: str) -> str:
    cipher = Fernet(derive_encryption_key(master_key))
    return cipher.encrypt(secret.encode("utf-8")).decode("ascii")


def decrypt_totp_secret(encrypted_secret: str, master_key: str) -> str:
    cipher = Fernet(derive_encryption_key(master_key))

    try:
        return cipher.decrypt(
            encrypted_secret.encode("ascii")
        ).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Unable to decrypt TOTP secret") from exc


def generate_provisioning_uri(secret: str, email: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name="Capstone Core",
    )


def verify_totp_code(
    secret: str,
    code: str,
    last_used_step: int | None = None,
    valid_window: int = 1,
) -> int | None:
    """Return accepted time step, or None for invalid/replayed codes."""
    if not isinstance(code, str) or len(code) != 6 or not code.isascii():
        return None

    if not code.isdigit():
        return None

    totp = pyotp.TOTP(secret)
    current_step = int(time.time()) // totp.interval

    for step in range(
        current_step - valid_window,
        current_step + valid_window + 1,
    ):
        if step < 0:
            continue

        expected = totp.at(step * totp.interval)

        if hmac.compare_digest(expected, code):
            if last_used_step is not None and step <= last_used_step:
                return None
            return step

    return None
