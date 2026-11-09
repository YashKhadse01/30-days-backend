
import base64
import json
import time

import httpx
import pytest

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import (
    padding,
    rsa,
)

from oauth_by_hand.google_identity import verify_google_id_token


CLIENT_ID = "test-google-client-id"
KEY_ID = "test-google-key"


def encode_bytes(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


@pytest.fixture
def rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_numbers = private_key.public_key().public_numbers()

    jwk = {
        "kty": "RSA",
        "kid": KEY_ID,
        "use": "sig",
        "alg": "RS256",
        "n": encode_bytes(
            public_numbers.n.to_bytes(
                (public_numbers.n.bit_length() + 7) // 8,
                "big",
            )
        ),
        "e": encode_bytes(
            public_numbers.e.to_bytes(
                (public_numbers.e.bit_length() + 7) // 8,
                "big",
            )
        ),
    }

    return private_key, jwk


@pytest.fixture
def mock_google_jwks(monkeypatch, rsa_keys):
    _, jwk = rsa_keys

    async def fake_get(self, url):
        assert url == "https://www.googleapis.com/oauth2/v3/certs"
        return httpx.Response(
            200,
            json={"keys": [jwk]},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)


def create_token(private_key, overrides=None):
    now = int(time.time())

    header = {
        "alg": "RS256",
        "typ": "JWT",
        "kid": KEY_ID,
    }

    payload = {
        "iss": "https://accounts.google.com",
        "aud": CLIENT_ID,
        "sub": "google-user-123",
        "iat": now,
        "exp": now + 3600,
        "nonce": "test-nonce",
    }

    if overrides:
        payload.update(overrides)

    header_part = encode_bytes(
        json.dumps(header).encode("utf-8")
    )
    payload_part = encode_bytes(
        json.dumps(payload).encode("utf-8")
    )

    signing_input = f"{header_part}.{payload_part}"

    signature = private_key.sign(
        signing_input.encode("ascii"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )

    return f"{signing_input}.{encode_bytes(signature)}"


@pytest.mark.asyncio
async def test_valid_google_token(rsa_keys, mock_google_jwks):
    private_key, _ = rsa_keys
    token = create_token(private_key)

    result = await verify_google_id_token(
        token,
        CLIENT_ID,
        expected_nonce="test-nonce",
    )

    assert result["sub"] == "google-user-123"


@pytest.mark.asyncio
async def test_wrong_audience_rejected(rsa_keys, mock_google_jwks):
    private_key, _ = rsa_keys
    token = create_token(private_key, {"aud": "wrong-client"})

    with pytest.raises(ValueError):
        await verify_google_id_token(token, CLIENT_ID)


@pytest.mark.asyncio
async def test_expired_token_rejected(rsa_keys, mock_google_jwks):
    private_key, _ = rsa_keys
    token = create_token(
        private_key,
        {"exp": int(time.time()) - 60},
    )

    with pytest.raises(ValueError):
        await verify_google_id_token(token, CLIENT_ID)


@pytest.mark.asyncio
async def test_wrong_issuer_rejected(rsa_keys, mock_google_jwks):
    private_key, _ = rsa_keys
    token = create_token(
        private_key,
        {"iss": "https://fake-google.example"},
    )

    with pytest.raises(ValueError):
        await verify_google_id_token(token, CLIENT_ID)


@pytest.mark.asyncio
async def test_wrong_nonce_rejected(rsa_keys, mock_google_jwks):
    private_key, _ = rsa_keys
    token = create_token(private_key)

    with pytest.raises(ValueError):
        await verify_google_id_token(
            token,
            CLIENT_ID,
            expected_nonce="wrong-nonce",
        )


@pytest.mark.asyncio
async def test_tampered_signature_rejected(
    rsa_keys,
    mock_google_jwks,
):
    private_key, _ = rsa_keys
    token = create_token(private_key)

    parts = token.split(".")
    signature = bytearray(
        base64.urlsafe_b64decode(
            parts[2] + "=" * (-len(parts[2]) % 4)
        )
    )
    signature[0] ^= 1
    parts[2] = encode_bytes(bytes(signature))
    tampered_token = ".".join(parts)

    with pytest.raises(Exception):
        await verify_google_id_token(
            tampered_token,
            CLIENT_ID,
        )


@pytest.mark.asyncio
async def test_missing_subject_rejected(rsa_keys, mock_google_jwks):
    private_key, _ = rsa_keys
    token = create_token(private_key, {"sub": ""})

    with pytest.raises(ValueError):
        await verify_google_id_token(token, CLIENT_ID)
