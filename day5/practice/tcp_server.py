import socket

HOST = "127.0.0.1"
PORT = 9000

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
        server.listen(1)

        print(f"TCP server running on {HOST}:{PORT}")
        print("Waiting for a client...")

        connection, address = server.accept()

        with connection:
            print(f"Connected by: {address}")

            data = connection.recv(1024)

            print(f"Received: {data.decode('utf-8')}")

            connection.sendall(
                b"Hello from Python TCP Server!"
            )

if __name__ == "__main__":
    main()
