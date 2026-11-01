from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

class MiniApp:
    def __init__(self) -> None:
        self.routes: dict[
            tuple[str, str], Callable[..., Any]
        ] = {}

    def route(
        self,
        path: str,
        method: str = "GET",
    ) -> Callable[
        [Callable[P, R]], Callable[P, R]
    ]:

        def decorator(
            func: Callable[P, R],
        ) -> Callable[P, R]:

            @wraps(func)
            def wrapper(
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> R:
                return func(*args, **kwargs)

            self.routes[(method.upper(), path)] = wrapper
            return wrapper

        return decorator

    def get(
        self,
        path: str,
    ) -> Callable[
        [Callable[P, R]], Callable[P, R]
    ]:
        return self.route(path, method="GET")

    def post(
        self,
        path: str,
    ) -> Callable[
        [Callable[P, R]], Callable[P, R]
    ]:
        return self.route(path, method="POST")

    def dispatch(
        self,
        method: str,
        path: str,
    ) -> Any:
        handler = self.routes.get((method.upper(), path))

        if handler is None:
            return {"error": "Route not found"}

        return handler()

app = MiniApp()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}

@app.get("/todos")
def list_todos() -> dict[str, Any]:
    return {
        "todos": [
            {"id": 1, "title": "Learn decorators"},
            {"id": 2, "title": "Build mini framework"},
        ]
    }

@app.post("/todos")
def create_todo() -> dict[str, str]:
    return {"message": "Todo created successfully"}

if __name__ == "__main__":
    print("REGISTERED ROUTES:")
    for method, path in app.routes:
        print(f"{method} {path}")

    print("\nTEST RESULTS:")
    print("TEST 1:", app.dispatch("GET", "/health"))
    print("TEST 2:", app.dispatch("GET", "/todos"))
    print("TEST 3:", app.dispatch("POST", "/todos"))
    print("TEST 4:", app.dispatch("GET", "/unknown"))
    print("TEST 5:", app.dispatch("DELETE", "/todos"))
