import socket
import json

HOST = "127.0.0.1"
PORT = 8000

def main() -> None:
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as server:

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server.bind((HOST, PORT))
        server.listen(5)

        print(f"HTTP server running at http://{HOST}:{PORT}")
        print("Press Ctrl+C to stop.")

        while True:
            connection, address = server.accept()

            with connection:
                print(f"\nClient connected: {address}")

                request = connection.recv(4096)

                if not request:
                    continue

                print("HTTP Request:")
                print(
                    request.decode(
                        "utf-8",
                        errors="replace"
                    )
                )

                data = {
                    "message": "Hello from Python Raw HTTP Server!",
                    "status": "success",
                    "day": 5
                }

                body = json.dumps(data).encode("utf-8")

                headers = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json; charset=utf-8\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("utf-8")

                connection.sendall(headers + body)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped.")
