import hashlib
import hmac
import json

from jwt_from_scratch.encoding import (
    base64url_decode,
    base64url_encode,
    json_to_base64url,
)


def sign_hs256(
    payload: dict,
    secret_key: str,
) -> str:
    """Create a JWT signed using HMAC-SHA256."""

    if not secret_key:
        raise ValueError("Secret key cannot be empty")

    header = {
        "alg": "HS256",
        "typ": "JWT",
    }

    encoded_header = json_to_base64url(header)
    encoded_payload = json_to_base64url(payload)

    signing_input = (
        f"{encoded_header}.{encoded_payload}"
    )

    signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()

    encoded_signature = base64url_encode(signature)

    return f"{signing_input}.{encoded_signature}"

def verify_hs256(
    token: str,
    secret_key: str,
) -> dict:
    """Verify HS256 signature and return the payload."""

    if not secret_key:
        raise ValueError("Secret key cannot be empty")

    try:
        encoded_header, encoded_payload, encoded_signature = (
            token.split(".")
        )

        header = json.loads(
            base64url_decode(encoded_header)
        )

        if not isinstance(header, dict):
            raise ValueError("Invalid JWT header")

        if header.get("alg") != "HS256":
            raise ValueError("Unsupported JWT algorithm")

        if header.get("typ") != "JWT":
            raise ValueError("Invalid JWT type")

        signing_input = (
            f"{encoded_header}.{encoded_payload}"
        )

        expected_signature = hmac.new(
            secret_key.encode("utf-8"),
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()

        received_signature = base64url_decode(
            encoded_signature
        )

        if not hmac.compare_digest(
            expected_signature,
            received_signature,
        ):
            raise ValueError("Invalid JWT signature")

        payload = json.loads(
            base64url_decode(encoded_payload)
        )

        if not isinstance(payload, dict):
            raise ValueError("Invalid JWT payload")

        return payload

    except (ValueError, UnicodeError, TypeError) as exc:
        raise ValueError("Invalid JWT") from exc
