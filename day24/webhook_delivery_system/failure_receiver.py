
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class FailureReceiver(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/webhook/":
            self.send_error(404)
            return

        print("Simulated HTTP 500 failure")

        self.send_response(500)
        self.send_header("Content-Length", "0")
        self.end_headers()


if __name__ == "__main__":
    server = ThreadingHTTPServer(
        ("127.0.0.1", 9001),
        FailureReceiver,
    )

    print("Failure receiver running on port 9001")
    server.serve_forever()
