
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from jwt_from_scratch.encoding import (
    base64url_decode,
    base64url_encode,
    json_to_base64url,
)


def generate_rsa_key_pair():
    """Generate an RSA private/public key pair."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=3072,
    )
    return private_key, private_key.public_key()


def sign_rs256(payload: dict, private_key) -> str:
    """Sign a JWT using an RSA private key."""
    header = {"alg": "RS256", "typ": "JWT"}

    encoded_header = json_to_base64url(header)
    encoded_payload = json_to_base64url(payload)

    signing_input = f"{encoded_header}.{encoded_payload}"

    signature = private_key.sign(
        signing_input.encode("ascii"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )

    return f"{signing_input}.{base64url_encode(signature)}"


def verify_rs256(token: str, public_key) -> dict:
    """Verify an RS256 signature and return its payload."""
    try:
        header_part, payload_part, signature_part = token.split(".")

        header = json.loads(base64url_decode(header_part))

        if not isinstance(header, dict):
            raise ValueError("Invalid JWT header")

        if header.get("alg") != "RS256":
            raise ValueError("Unsupported JWT algorithm")

        if header.get("typ") != "JWT":
            raise ValueError("Invalid JWT type")

        signing_input = f"{header_part}.{payload_part}"

        signature = base64url_decode(signature_part)

        public_key.verify(
            signature,
            signing_input.encode("ascii"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

        payload = json.loads(base64url_decode(payload_part))

        if not isinstance(payload, dict):
            raise ValueError("Invalid JWT payload")

        return payload

    except (
        InvalidSignature,
        ValueError,
        TypeError,
        UnicodeError,
    ) as exc:
        raise ValueError("Invalid JWT") from exc
