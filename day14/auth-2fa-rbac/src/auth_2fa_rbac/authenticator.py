
from urllib.parse import urlencode

import qrcode

from auth_2fa_rbac.totp import generate_totp_secret


def generate_provisioning_uri(
    secret: str,
    account_name: str,
    issuer: str = "Day14Backend",
) -> str:
    """Create a Google Authenticator-compatible TOTP URI."""
    if not secret or not account_name or not issuer:
        raise ValueError("Secret, account and issuer are required")

    label = f"{issuer}:{account_name}"

    params = urlencode({
        "secret": secret,
        "issuer": issuer,
        "algorithm": "SHA1",
        "digits": 6,
        "period": 30,
    })

    from urllib.parse import quote
    return f"otpauth://totp/{quote(label, safe='')}?{params}"


def create_qr_code(uri: str, filename: str) -> None:
    """Save an authenticator QR code locally."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )
    image.save(filename)
