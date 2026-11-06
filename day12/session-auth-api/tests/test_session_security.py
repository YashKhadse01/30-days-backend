
from datetime import datetime, timezone

from session_auth_api.csrf import (
    generate_csrf_token,
    validate_csrf_token,
)
from session_auth_api.sessions import (
    generate_session_token,
    hash_session_token,
)


def test_session_tokens_are_unique():
    first = generate_session_token()
    second = generate_session_token()

    assert first != second
    assert hash_session_token(first) != hash_session_token(second)


def test_csrf_token_bound_to_session():
    secret = "test-secret-key"
    session_a = generate_session_token()
    session_b = generate_session_token()

    csrf_token = generate_csrf_token(session_a, secret)

    assert validate_csrf_token(
        session_a, csrf_token, secret
    )

    assert not validate_csrf_token(
        session_b, csrf_token, secret
    )


def test_csrf_token_tampering_rejected():
    session = generate_session_token()
    token = generate_csrf_token(session, "test-secret-key")

    nonce, signature = token.split(".")
    tampered_signature = (
        ("0" if signature[0] != "0" else "1")
        + signature[1:]
    )

    assert not validate_csrf_token(
        session,
        f"{nonce}.{tampered_signature}",
        "test-secret-key",
    )
