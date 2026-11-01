from http.server import BaseHTTPRequestHandler, HTTPServer
from http import HTTPStatus
from urllib.parse import urlsplit
from app import Request
from main import app

class MiniHTTPHandler(BaseHTTPRequestHandler):
    def handle_request(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)

        request = Request(
            method=self.command,
            path=urlsplit(self.path).path,
            headers=dict(self.headers),
            body=body,
        )

        response = app.dispatch(request)
        response_bytes = response.to_bytes()

        self.send_response(response.status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_GET(self) -> None:
        self.handle_request()

    def do_POST(self) -> None:
        self.handle_request()

    def do_PUT(self) -> None:
        self.handle_request()

    def do_DELETE(self) -> None:
        self.handle_request()

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8007), MiniHTTPHandler)

    print("Mini Framework running at http://127.0.0.1:8007")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
