from collections.abc import Callable
from typing import Any

class Router:
    def __init__(self) -> None:
        self.routes: list[
            tuple[str, str, Callable[..., Any]]
        ] = []

    def add_route(
        self,
        method: str,
        path: str,
        handler: Callable[..., Any],
    ) -> None:
        self.routes.append(
            (method.upper(), path, handler)
        )

    def match(
        self,
        method: str,
        path: str,
    ) -> tuple[Callable[..., Any], dict[str, Any]] | None:

        for route_method, route_path, handler in self.routes:

            if route_method != method.upper():
                continue

            expected_parts = route_path.strip("/").split("/")
            actual_parts = path.strip("/").split("/")

            if len(expected_parts) != len(actual_parts):
                continue

            params: dict[str, Any] = {}
            matched = True

            for expected, actual in zip(
                expected_parts, actual_parts
            ):
                if expected.startswith("{") and expected.endswith("}"):
                    param_name = expected[1:-1]

                    if not actual.isdigit():
                        matched = False
                        break

                    params[param_name] = int(actual)

                elif expected != actual:
                    matched = False
                    break

            if matched:
                return handler, params

        return None

    def dispatch(
        self,
        method: str,
        path: str,
    ) -> dict[str, Any]:

        result = self.match(method, path)

        if result is None:
            return {"error": "Route not found"}

        handler, params = result
        return handler(**params)

router = Router()

def health() -> dict[str, Any]:
    return {"status": "healthy"}

def list_todos() -> dict[str, Any]:
    return {
        "todos": [
            {"id": 1, "title": "Learn Python"},
            {"id": 2, "title": "Build Mini Framework"},
        ]
    }

def get_todo(todo_id: int) -> dict[str, Any]:
    return {
        "todo": {
            "id": todo_id,
            "title": f"Todo number {todo_id}",
        }
    }

router.add_route("GET", "/health", health)
router.add_route("GET", "/todos", list_todos)
router.add_route("GET", "/todos/{todo_id}", get_todo)

if __name__ == "__main__":
    print("TEST 1:", router.dispatch("GET", "/health"))

    print("TEST 2:", router.dispatch("GET", "/todos"))

    print("TEST 3:", router.dispatch("GET", "/todos/1"))

    print("TEST 4:", router.dispatch("GET", "/todos/25"))

    print("TEST 5:", router.dispatch("GET", "/unknown"))

    print("TEST 6:", router.dispatch("GET", "/todos/abc"))
