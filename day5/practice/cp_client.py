import socket

HOST = "127.0.0.1"
PORT = 9000

def main() -> None:
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as client:

        client.connect((HOST, PORT))

        client.sendall(b"Hello Server!")

        response = client.recv(1024)

        print(response.decode("utf-8"))

if __name__ == "__main__":
    main()
