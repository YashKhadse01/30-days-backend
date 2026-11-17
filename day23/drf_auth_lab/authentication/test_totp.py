
import pyotp
from django.test import SimpleTestCase

from authentication.totp_utils import (
    generate_totp_secret,
    generate_totp_uri,
    verify_totp,
)


class TOTPTests(SimpleTestCase):
    def setUp(self):
        self.secret = generate_totp_secret()

    def test_secret_generation(self):
        self.assertTrue(self.secret)

    def test_provisioning_uri(self):
        uri = generate_totp_uri(
            self.secret,
            "test_user",
        )
        self.assertTrue(uri.startswith("otpauth://"))

    def test_valid_totp(self):
        code = pyotp.TOTP(self.secret).now()
        self.assertTrue(verify_totp(self.secret, code))

    def test_invalid_totp(self):
        self.assertFalse(
            verify_totp(self.secret, "invalid")
        )

    def test_missing_totp(self):
        self.assertFalse(
            verify_totp(self.secret, "")
        )
