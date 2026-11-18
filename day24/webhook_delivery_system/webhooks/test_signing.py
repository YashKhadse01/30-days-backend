
import time

from django.test import SimpleTestCase

from webhooks.signing import create_signature, verify_signature


class WebhookSigningTests(SimpleTestCase):
    def setUp(self):
        self.secret = "development-test-secret"
        self.payload = b'{"event":"order.created","id":123}'
        self.timestamp = str(int(time.time()))

    def test_valid_signature(self):
        signature = create_signature(
            self.secret,
            self.timestamp,
            self.payload,
        )

        self.assertTrue(
            verify_signature(
                self.secret,
                self.timestamp,
                self.payload,
                signature,
            )
        )

    def test_modified_payload_rejected(self):
        signature = create_signature(
            self.secret,
            self.timestamp,
            self.payload,
        )

        self.assertFalse(
            verify_signature(
                self.secret,
                self.timestamp,
                b'{"event":"order.deleted","id":123}',
                signature,
            )
        )

    def test_invalid_signature_rejected(self):
        self.assertFalse(
            verify_signature(
                self.secret,
                self.timestamp,
                self.payload,
                "invalid-signature",
            )
        )

    def test_expired_timestamp_rejected(self):
        old_timestamp = str(int(time.time()) - 600)
        signature = create_signature(
            self.secret,
            old_timestamp,
            self.payload,
        )

        self.assertFalse(
            verify_signature(
                self.secret,
                old_timestamp,
                self.payload,
                signature,
            )
        )

    def test_future_timestamp_rejected(self):
        future_timestamp = str(int(time.time()) + 600)
        signature = create_signature(
            self.secret,
            future_timestamp,
            self.payload,
        )

        self.assertFalse(
            verify_signature(
                self.secret,
                future_timestamp,
                self.payload,
                signature,
            )
        )
