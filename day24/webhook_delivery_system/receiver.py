
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from webhooks.signing import verify_signature

HOST = "127.0.0.1"
PORT = 9000
SECRET = os.environ.get("WEBHOOK_RECEIVER_SECRET")

if not SECRET:
    raise RuntimeError("WEBHOOK_RECEIVER_SECRET is required")

processed_events = set()
event_lock = threading.Lock()


class WebhookReceiver(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/webhook/":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return

        if not 0 < length <= 1_000_000:
            self.send_error(400, "Invalid body length")
            return

        body = self.rfile.read(length)

        timestamp = self.headers.get("X-Webhook-Timestamp", "")
        signature = self.headers.get("X-Webhook-Signature", "")
        event_id = self.headers.get("X-Webhook-ID", "")

        if not verify_signature(
            SECRET, timestamp, body, signature
        ):
            self.send_error(401, "Invalid webhook signature")
            return

        try:
            event = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(400, "Invalid JSON")
            return

        if not isinstance(event, dict):
            self.send_error(400, "Invalid event")
            return

        if not event_id or event.get("id") != event_id:
            self.send_error(400, "Event ID mismatch")
            return

        with event_lock:
            if event_id in processed_events:
                self.send_json(200, {"status": "duplicate"})
                return

            processed_events.add(event_id)

        print("Received event:", event.get("type"), event_id)
        self.send_json(200, {"status": "received"})

    def send_json(self, status, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), WebhookReceiver)
    print(f"Webhook receiver listening on http://{HOST}:{PORT}/webhook/")
    server.serve_forever()
