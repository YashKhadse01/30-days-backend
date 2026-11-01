from dataclasses import dataclass, field
import json
from typing import Any


@dataclass
class Request:
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    def json(self) -> Any:
        if not self.body:
            return None
        return json.loads(self.body)


@dataclass
class Response:
    body: dict[str, Any]
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)

    def to_http(self) -> bytes:
        body_bytes = json.dumps(self.body).encode("utf-8")

        reasons = {
            200: "OK",
            201: "Created",
            400: "Bad Request",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error",
        }

        reason = reasons.get(self.status_code, "Unknown")

        response_headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": str(len(body_bytes)),
            "Connection": "close",
            **self.headers,
        }

        header_lines = [
            f"HTTP/1.1 {self.status_code} {reason}",
            *[
                f"{name}: {value}"
                for name, value in response_headers.items()
            ],
        ]

        header_text = "\r\n".join(header_lines) + "\r\n\r\n"

        return header_text.encode("utf-8") + body_bytes


if __name__ == "__main__":
    request = Request(
        method="POST",
        path="/todos",
        headers={"Content-Type": "application/json"},
        body=b'{"title": "Learn Python Frameworks"}',
    )

    print("REQUEST METHOD:", request.method)
    print("REQUEST PATH:", request.path)
    print("REQUEST JSON:", request.json())

    response = Response(
        body={
            "message": "Todo created",
            "title": request.json()["title"],
        },
        status_code=201,
    )

    print("\nHTTP RESPONSE:")
    print(response.to_http().decode("utf-8"))
