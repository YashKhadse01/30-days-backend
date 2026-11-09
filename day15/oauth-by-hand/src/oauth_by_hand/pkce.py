
import base64
import hashlib
import secrets


def generate_code_verifier() -> str:
    """Generate a secure RFC 7636 PKCE verifier."""
    return secrets.token_urlsafe(32)


def generate_code_challenge(verifier: str) -> str:
    """Generate an S256 PKCE challenge."""
    digest = hashlib.sha256(
        verifier.encode("ascii")
    ).digest()

    return base64.urlsafe_b64encode(
        digest
    ).rstrip(b"=").decode("ascii")


def verify_code_challenge(
    verifier: str,
    challenge: str,
) -> bool:
    """Verify a PKCE S256 challenge."""
    expected = generate_code_challenge(verifier)

    return secrets.compare_digest(
        expected,
        challenge,
    )
