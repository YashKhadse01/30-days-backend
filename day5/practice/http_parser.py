import socket
import json

HOST = "127.0.0.1"
PORT = 8002
MAX_BODY_SIZE = 1_000_000

def read_request(
    connection: socket.socket,
) -> tuple[str, str, dict[str, str], bytes]:

    connection.settimeout(5)

    buffer = b""

    # Read until the HTTP header section is complete
    while b"\r\n\r\n" not in buffer:
        chunk = connection.recv(4096)

        if not chunk:
            raise ValueError("Incomplete HTTP headers")

        buffer += chunk

        if len(buffer) > 65536:
            raise ValueError("Headers too large")

    header_bytes, body = buffer.split(b"\r\n\r\n", 1)

    lines = header_bytes.decode("iso-8859-1").split("\r\n")

    method, path, version = lines[0].split()

    if not version.startswith("HTTP/"):
        raise ValueError("Invalid HTTP version")

    headers: dict[str, str] = {}

    for line in lines[1:]:
        if ":" not in line:
            raise ValueError("Invalid header")

        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    content_length = int(headers.get("content-length", "0"))

    if content_length < 0 or content_length > MAX_BODY_SIZE:
        raise ValueError("Invalid Content-Length")

    # Read the remaining request body
    while len(body) < content_length:
        chunk = connection.recv(
            min(4096, content_length - len(body))
        )

        if not chunk:
            raise ValueError("Incomplete request body")

        body += chunk

    return method, path, headers, body[:content_length]

def send_json(
    connection: socket.socket,
    status: int,
    message: str,
    data: dict[str, object],
) -> None:

    body = json.dumps(data).encode("utf-8")

    response = (
        f"HTTP/1.1 {status} {message}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8") + body

    connection.sendall(response)

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

        print(f"Server running at http://{HOST}:{PORT}")

        while True:
            connection, address = server.accept()

            with connection:
                try:
                    method, path, headers, body = read_request(
                        connection
                    )

                    print(f"\nClient: {address}")
                    print(f"Method: {method}")
                    print(f"Path: {path}")
                    print(f"Headers: {headers}")
                    print(f"Body: {body.decode('utf-8', errors='replace')}")

                    send_json(
                        connection,
                        200,
                        "OK",
                        {
                            "method": method,
                            "path": path,
                            "body_size": len(body),
                        },
                    )

                except (ValueError, UnicodeError, socket.timeout) as error:
                    print(f"Invalid request: {error}")

                    try:
                        send_json(
                            connection,
                            400,
                            "Bad Request",
                            {"error": "Invalid HTTP request"},
                        )
                    except OSError:
                        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped.")
