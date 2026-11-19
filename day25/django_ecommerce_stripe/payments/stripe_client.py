import stripe
from django.conf import settings


def get_stripe_client():
    """Return a Stripe client configured for test mode."""

    secret_key = settings.STRIPE_SECRET_KEY

    if not secret_key.startswith("sk_test_"):
        raise ValueError(
            "A valid Stripe test-mode secret key is required."
        )

    return stripe.StripeClient(secret_key)