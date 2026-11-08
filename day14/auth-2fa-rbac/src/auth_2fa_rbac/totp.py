
import base64
import hashlib
import hmac
import secrets
import struct
import time


def generate_totp_secret() -> str:
    """Generate a cryptographically secure Base32 secret."""
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii")


def generate_totp(
    secret: str,
    timestamp: int | None = None,
    interval: int = 30,
    digits: int = 6,
) -> str:
    """Generate an RFC 6238 TOTP using HMAC-SHA1."""
    if interval <= 0 or not 1 <= digits <= 10:
        raise ValueError("Invalid TOTP parameters")

    if timestamp is None:
        timestamp = int(time.time())

    if timestamp < 0:
        raise ValueError("Invalid timestamp")

    try:
        key = base64.b32decode(secret, casefold=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ValueError("Invalid TOTP secret") from exc

    counter = timestamp // interval
    message = struct.pack(">Q", counter)

    digest = hmac.new(key, message, hashlib.sha1).digest()

    offset = digest[-1] & 0x0F

    binary_code = (
        struct.unpack(">I", digest[offset:offset + 4])[0]
        & 0x7FFFFFFF
    )

    otp = binary_code % (10 ** digits)
    return str(otp).zfill(digits)

def verify_totp(
    secret: str,
    otp: str,
    timestamp: int | None = None,
    interval: int = 30,
    window: int = 1,
) -> bool:
    """Verify a TOTP within an allowed time window."""
    if not isinstance(otp, str) or len(otp) != 6 or not otp.isascii() or not otp.isdigit():
        return False

    if interval <= 0 or window < 0:
        raise ValueError("Invalid verification parameters")

    if timestamp is None:
        timestamp = int(time.time())

    if timestamp < 0:
        raise ValueError("Invalid timestamp")

    for offset in range(-window, window + 1):
        candidate_time = timestamp + offset * interval

        if candidate_time < 0:
            continue

        expected = generate_totp(
            secret,
            timestamp=candidate_time,
            interval=interval,
        )

        if hmac.compare_digest(expected, otp):
            return True

    return False
