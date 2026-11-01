from dataclasses import dataclass, field
from collections.abc import Callable
from typing import Any
import json
import re

@dataclass
class Request:
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    def json(self) -> Any:
        return json.loads(self.body)

@dataclass
class Response:
    body: dict[str, Any]
    status_code: int = 200

    def to_bytes(self) -> bytes:
        return json.dumps(self.body).encode("utf-8")

class MiniApp:
    def __init__(self) -> None:
        self.routes: list[
            tuple[str, str, Callable[..., Response]]
        ] = []

    def route(self, method: str, path: str):
        def decorator(func: Callable[..., Response]):
            self.routes.append((method.upper(), path, func))
            return func

        return decorator

    def get(self, path: str):
        return self.route("GET", path)

    def post(self, path: str):
        return self.route("POST", path)

    def put(self, path: str):
        return self.route("PUT", path)

    def delete(self, path: str):
        return self.route("DELETE", path)

    def dispatch(self, request: Request) -> Response:
        for method, route_path, handler in self.routes:
            pattern = re.sub(
                r"\{(\w+)\}",
                r"(?P<\1>[0-9]+)",
                route_path,
            )

            match = re.fullmatch(pattern, request.path)

            if match and method == request.method.upper():
                params = {
                    key: int(value)
                    for key, value in match.groupdict().items()
                }

                try:
                    return handler(request, **params)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return Response(
                        {"error": "Invalid JSON"},
                        status_code=400,
                    )

        return Response(
            {"error": "Route not found"},
            status_code=404,
        )
