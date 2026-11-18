
import json
import os
import threading
import time
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import requests

from webhooks.signing import create_signature


class ReceiverSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.secret = "day24-receiver-test-secret"
        cls.secret_patch = patch.dict(
            os.environ,
            {"WEBHOOK_RECEIVER_SECRET": cls.secret},
        )
        cls.secret_patch.start()

        from receiver import WebhookReceiver

        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            WebhookReceiver,
        )

        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.thread.start()

        cls.url = (
            f"http://127.0.0.1:{cls.server.server_port}/webhook/"
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.secret_patch.stop()
        super().tearDownClass()

    def send_event(
        self,
        event_id,
        *,
        secret=None,
        timestamp=None,
        signature=None,
    ):
        body = json.dumps(
            {
                "id": event_id,
                "type": "order.created",
                "data": {"order_id": 101},
            },
            separators=(",", ":"),
        ).encode("utf-8")

        timestamp = timestamp or str(int(time.time()))

        if signature is None:
            signature = create_signature(
                secret or self.secret,
                timestamp,
                body,
            )

        return requests.post(
            self.url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Webhook-ID": event_id,
                "X-Webhook-Timestamp": timestamp,
                "X-Webhook-Signature": signature,
            },
            timeout=5,
        )

    def test_valid_signature_accepted(self):
        response = self.send_event("receiver-test-valid")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "received")

    def test_invalid_signature_rejected(self):
        response = self.send_event(
            "receiver-test-invalid",
            signature="invalid-signature",
        )
        self.assertEqual(response.status_code, 401)

    def test_expired_timestamp_rejected(self):
        timestamp = str(int(time.time()) - 600)

        response = self.send_event(
            "receiver-test-expired",
            timestamp=timestamp,
        )
        self.assertEqual(response.status_code, 401)

    def test_duplicate_event_is_idempotent(self):
        event_id = "receiver-test-duplicate"

        first = self.send_event(event_id)
        second = self.send_event(event_id)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["status"], "received")

        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["status"], "duplicate")

    def test_wrong_secret_rejected(self):
        response = self.send_event(
            "receiver-test-wrong-secret",
            secret="incorrect-secret",
        )
        self.assertEqual(response.status_code, 401)
