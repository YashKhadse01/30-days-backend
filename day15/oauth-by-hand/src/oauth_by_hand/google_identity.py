
import base64
import json
import time

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import (
    padding,
    rsa,
)


GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"

VALID_ISSUERS = {
    "https://accounts.google.com",
    "accounts.google.com",
}


def decode_bytes(segment: str) -> bytes:
    """Decode a Base64URL-encoded JWT segment."""
    padded = segment + "=" * (-len(segment) % 4)
    return base64.b64decode(
        padded,
        altchars=b"-_",
        validate=True,
    )


def decode_segment(segment: str) -> dict:
    """Decode a JWT JSON segment."""
    raw = decode_bytes(segment)
    value = json.loads(raw)

    if not isinstance(value, dict):
        raise ValueError("Invalid JWT JSON object")

    return value


async def verify_google_id_token(
    id_token: str,
    client_id: str,
    *,
    expected_nonce: str | None = None,
) -> dict:
    """Verify Google's RS256-signed OpenID Connect ID token."""

    if not id_token or not client_id:
        raise ValueError("ID token and client ID required")

    try:
        parts = id_token.split(".")

        if len(parts) != 3:
            raise ValueError("Malformed ID token")

        header_part, payload_part, signature_part = parts

        header = decode_segment(header_part)
        payload = decode_segment(payload_part)

        if header.get("alg") != "RS256":
            raise ValueError("Unsupported ID token algorithm")

        kid = header.get("kid")

        if not isinstance(kid, str) or not kid:
            raise ValueError("Missing key ID")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(GOOGLE_JWKS_URL)
            response.raise_for_status()
            jwks = response.json()

        matching_keys = [
            key
            for key in jwks["keys"]
            if key.get("kid") == kid
            and key.get("kty") == "RSA"
            and key.get("use", "sig") == "sig"
            and key.get("alg", "RS256") == "RS256"
        ]

        if len(matching_keys) != 1:
            raise ValueError("Google signing key not found")

        jwk = matching_keys[0]

        n = int.from_bytes(
            decode_bytes(jwk["n"]),
            "big",
        )
        e = int.from_bytes(
            decode_bytes(jwk["e"]),
            "big",
        )

        public_key = rsa.RSAPublicNumbers(
            e,
            n,
        ).public_key()

        public_key.verify(
            decode_bytes(signature_part),
            f"{header_part}.{payload_part}".encode("ascii"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

        now = time.time()

        if payload.get("iss") not in VALID_ISSUERS:
            raise ValueError("Invalid Google issuer")

        if payload.get("aud") != client_id:
            raise ValueError("Invalid token audience")

        exp = payload.get("exp")
        iat = payload.get("iat")

        if (
            type(exp) is not int
            or type(iat) is not int
            or exp <= now
            or iat > now
        ):
            raise ValueError("Invalid token timestamps")

        sub = payload.get("sub")

        if not isinstance(sub, str) or not sub:
            raise ValueError("Missing Google subject")

        if expected_nonce is not None:
            if payload.get("nonce") != expected_nonce:
                raise ValueError("Invalid OIDC nonce")

        return payload

    except (
        InvalidSignature,
        KeyError,
        TypeError,
        IndexError,
        ValueError,
        UnicodeError,
    ) as exc:
        raise ValueError("Invalid Google ID token") from exc
