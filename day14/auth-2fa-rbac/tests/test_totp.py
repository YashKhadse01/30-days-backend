
import base64

import pytest

from auth_2fa_rbac.totp import generate_totp, verify_totp


# RFC 6238 Appendix B test secret for SHA-1.
RFC_SECRET = base64.b32encode(
    b"12345678901234567890"
).decode("ascii")


@pytest.mark.parametrize(
    ("timestamp", "expected"),
    [
        (59, "94287082"),
        (1111111109, "07081804"),
        (1111111111, "14050471"),
        (1234567890, "89005924"),
        (2000000000, "69279037"),
        (20000000000, "65353130"),
    ],
)
def test_rfc6238_sha1_vectors(timestamp, expected):
    assert generate_totp(
        RFC_SECRET,
        timestamp=timestamp,
        digits=8,
    ) == expected


def test_valid_otp_accepted():
    timestamp = 1234567890
    otp = generate_totp(RFC_SECRET, timestamp)

    assert verify_totp(
        RFC_SECRET, otp, timestamp=timestamp
    )


def test_invalid_otp_rejected():
    assert not verify_totp(
        RFC_SECRET,
        "abcdef",
        timestamp=1234567890,
    )


def test_wrong_otp_rejected():
    timestamp = 1234567890
    correct = generate_totp(RFC_SECRET, timestamp)
    wrong = "000000" if correct != "000000" else "999999"

    assert not verify_totp(
        RFC_SECRET, wrong, timestamp=timestamp
    )


def test_adjacent_window_accepted():
    timestamp = 1234567890
    previous = generate_totp(
        RFC_SECRET, timestamp=timestamp - 30
    )

    assert verify_totp(
        RFC_SECRET,
        previous,
        timestamp=timestamp,
        window=1,
    )


def test_outside_window_rejected():
    timestamp = 1234567890
    old = generate_totp(
        RFC_SECRET, timestamp=timestamp - 90
    )

    assert not verify_totp(
        RFC_SECRET,
        old,
        timestamp=timestamp,
        window=1,
    )
