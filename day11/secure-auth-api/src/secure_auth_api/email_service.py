
import logging
from secure_auth_api.database import settings

logger = logging.getLogger(__name__)


def send_verification_email(email: str, token: str) -> None:
    """Print verification tokens only in local development."""

    if settings.app_env.lower() != "development":
        raise RuntimeError(
            "A production email provider is not configured"
        )

    logger.warning(
        "LOCAL DEVELOPMENT ONLY - Verification token for %s: %s",
        email,
        token,
    )
