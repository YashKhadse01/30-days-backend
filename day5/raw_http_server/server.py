import json
import socket
from app import handle_request

HOST = "127.0.0.1"
PORT = 8003

MAX_HEADER_SIZE = 65536
MAX_BODY_SIZE = 1_000_000

REASONS = {
    200: "OK",
    201: "Created",
    400: "Bad Request",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}

def read_request(
    connection: socket.socket,
) -> tuple[str, str, bytes]:
    connection.settimeout(5)
    buffer = b""

    while b"\r\n\r\n" not in buffer:
        chunk = connection.recv(4096)

        if not chunk:
            raise ValueError("Incomplete HTTP headers")

        buffer += chunk

        if len(buffer) > MAX_HEADER_SIZE + MAX_BODY_SIZE:
            raise ValueError("Request too large")

    header_bytes, body = buffer.split(b"\r\n\r\n", 1)

    if len(header_bytes) > MAX_HEADER_SIZE:
        raise ValueError("Headers too large")

    lines = header_bytes.decode("iso-8859-1").split("\r\n")

    parts = lines[0].split()

    if len(parts) != 3:
        raise ValueError("Invalid request line")

    method, target, version = parts

    if version not in ("HTTP/1.0", "HTTP/1.1"):
        raise ValueError("Unsupported HTTP version")

    headers: dict[str, str] = {}

    for line in lines[1:]:
        if ":" not in line:
            raise ValueError("Invalid HTTP header")

        key, value = line.split(":", 1)
        key = key.strip().lower()

        if key in headers:
            raise ValueError("Duplicate HTTP header")

        headers[key] = value.strip()

    if "transfer-encoding" in headers:
        raise ValueError("Transfer-Encoding is unsupported")

    try:
        content_length = int(headers.get("content-length", "0"))
    except ValueError:
        raise ValueError("Invalid Content-Length") from None

    if not 0 <= content_length <= MAX_BODY_SIZE:
        raise ValueError("Invalid body size")

    while len(body) < content_length:
        chunk = connection.recv(
            min(4096, content_length - len(body))
        )

        if not chunk:
            raise ValueError("Incomplete request body")

        body += chunk

    return method, target, body[:content_length]

def build_response(
    status: int,
    data: dict[str, object],
) -> bytes:
    body = json.dumps(data).encode("utf-8")
    reason = REASONS.get(status, "Unknown")

    headers = (
        f"HTTP/1.1 {status} {reason}\r\n"
        "Content-Type: application/json; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8")

    return headers + body

def main() -> None:
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as server:
        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )

        server.bind((HOST, PORT))
        server.listen(5)

        print(f"Raw HTTP API running at http://{HOST}:{PORT}")
        print("Press Ctrl+C to stop.")

        while True:
            connection, address = server.accept()

            with connection:
                try:
                    method, target, body = read_request(
                        connection
                    )

                    print(f"{address}: {method} {target}")

                    status, data = handle_request(
                        method,
                        target,
                        body,
                    )

                except (ValueError, socket.timeout) as error:
                    print(f"Bad request: {error}")
                    status = 400
                    data = {"error": "Invalid HTTP request"}

                try:
                    connection.sendall(
                        build_response(status, data)
                    )
                except OSError as error:
                    print(f"Connection error: {error}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped.")
