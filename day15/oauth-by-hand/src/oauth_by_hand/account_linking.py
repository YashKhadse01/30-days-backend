
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class LocalUser:
    user_id: str
    email: str
    google_subjects: set[str] = field(default_factory=set)


users: dict[str, LocalUser] = {}
google_accounts: dict[str, str] = {}


def create_local_user(email: str) -> LocalUser:
    """Create a local application user."""
    if not isinstance(email, str) or not email.strip():
        raise ValueError("Valid email required")

    user = LocalUser(
        user_id=str(uuid4()),
        email=email.strip(),
    )

    users[user.user_id] = user
    return user


def find_google_user(google_sub: str) -> LocalUser | None:
    """Find a user by Google's verified subject."""
    user_id = google_accounts.get(google_sub)

    if user_id is None:
        return None

    return users.get(user_id)


def login_or_register_google(
    verified_claims: dict,
) -> LocalUser:
    """
    Find or create a user after Google ID token verification.

    IMPORTANT: Caller must verify the ID token first.
    """
    google_sub = verified_claims.get("sub")

    if not isinstance(google_sub, str) or not google_sub:
        raise ValueError("Invalid Google subject")

    existing = find_google_user(google_sub)

    if existing is not None:
        return existing

    email = verified_claims.get("email", "")

    if not isinstance(email, str):
        email = ""

    user = create_local_user(
        email or f"google-{google_sub}@placeholder.invalid"
    )

    google_accounts[google_sub] = user.user_id
    user.google_subjects.add(google_sub)

    return user


def link_google_account(
    authenticated_user_id: str,
    verified_claims: dict,
) -> LocalUser:
    """
    Link Google to an authenticated local account.

    Caller must authenticate the local user and verify
    the Google ID token before calling this function.
    """
    user = users.get(authenticated_user_id)

    if user is None:
        raise ValueError("Authenticated local user required")

    google_sub = verified_claims.get("sub")

    if not isinstance(google_sub, str) or not google_sub:
        raise ValueError("Invalid Google subject")

    existing_user_id = google_accounts.get(google_sub)

    if (
        existing_user_id is not None
        and existing_user_id != authenticated_user_id
    ):
        raise ValueError("Google account already linked")

    google_accounts[google_sub] = user.user_id
    user.google_subjects.add(google_sub)

    return user

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class LocalUser:
    user_id: str
    email: str
    google_subjects: set[str] = field(default_factory=set)


users: dict[str, LocalUser] = {}
google_accounts: dict[str, str] = {}


def create_local_user(email: str) -> LocalUser:
    """Create a local application user."""
    if not isinstance(email, str) or not email.strip():
        raise ValueError("Valid email required")

    user = LocalUser(
        user_id=str(uuid4()),
        email=email.strip(),
    )

    users[user.user_id] = user
    return user


def find_google_user(google_sub: str) -> LocalUser | None:
    """Find a user by Google's verified subject."""
    user_id = google_accounts.get(google_sub)

    if user_id is None:
        return None

    return users.get(user_id)


def login_or_register_google(
    verified_claims: dict,
) -> LocalUser:
    """
    Find or create a user after Google ID token verification.

    IMPORTANT: Caller must verify the ID token first.
    """
    google_sub = verified_claims.get("sub")

    if not isinstance(google_sub, str) or not google_sub:
        raise ValueError("Invalid Google subject")

    existing = find_google_user(google_sub)

    if existing is not None:
        return existing

    email = verified_claims.get("email", "")

    if not isinstance(email, str):
        email = ""

    user = create_local_user(
        email or f"google-{google_sub}@placeholder.invalid"
    )

    google_accounts[google_sub] = user.user_id
    user.google_subjects.add(google_sub)

    return user


def link_google_account(
    authenticated_user_id: str,
    verified_claims: dict,
) -> LocalUser:
    """
    Link Google to an authenticated local account.

    Caller must authenticate the local user and verify
    the Google ID token before calling this function.
    """
    user = users.get(authenticated_user_id)

    if user is None:
        raise ValueError("Authenticated local user required")

    google_sub = verified_claims.get("sub")

    if not isinstance(google_sub, str) or not google_sub:
        raise ValueError("Invalid Google subject")

    existing_user_id = google_accounts.get(google_sub)

    if (
        existing_user_id is not None
        and existing_user_id != authenticated_user_id
    ):
        raise ValueError("Google account already linked")

    google_accounts[google_sub] = user.user_id
    user.google_subjects.add(google_sub)

    return user
