import re

def validate_password(password: str) -> str:
    """Validate a password against our registration policy."""

    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")

    if len(password) > 128:
        raise ValueError("Password must not exceed 128 characters")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain a number")

    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must contain a special character")

    return password