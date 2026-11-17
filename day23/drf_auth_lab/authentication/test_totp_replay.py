
import pyotp
from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import TOTPDevice
from authentication.totp_utils import verify_totp_once


class TOTPReplayTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="totp_replay_user",
            password="StrongTestPassword123!",
        )
        self.secret = pyotp.random_base32()
        self.device = TOTPDevice.objects.create(
            user=self.user,
            secret=self.secret,
            is_verified=True,
        )

    def test_valid_code_accepted(self):
        code = pyotp.TOTP(self.secret).now()
        self.assertTrue(verify_totp_once(self.user, code))

    def test_replayed_code_rejected(self):
        code = pyotp.TOTP(self.secret).now()

        self.assertTrue(verify_totp_once(self.user, code))
        self.assertFalse(verify_totp_once(self.user, code))

    def test_invalid_code_rejected(self):
        self.assertFalse(
            verify_totp_once(self.user, "invalid")
        )

    def test_unverified_device_rejected(self):
        self.device.is_verified = False
        self.device.save(update_fields=["is_verified"])

        code = pyotp.TOTP(self.secret).now()

        self.assertFalse(verify_totp_once(self.user, code))

    def test_missing_device_rejected(self):
        self.device.delete()

        self.assertFalse(
            verify_totp_once(self.user, "123456")
        )
