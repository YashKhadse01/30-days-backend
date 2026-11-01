from collections.abc import Callable

# A route maps an HTTP method and URL path to a function.
RouteHandler = Callable[[], dict[str, str]]

routes: dict[tuple[str, str], RouteHandler] = {}


def route(method: str, path: str) -> Callable[[RouteHandler], RouteHandler]:
    """Register a function as an HTTP route."""

    def decorator(func: RouteHandler) -> RouteHandler:
        routes[(method.upper(), path)] = func
        return func

    return decorator


@route("GET", "/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@route("GET", "/hello")
def hello() -> dict[str, str]:
    return {"message": "Hello from my mini framework!"}


def handle_request(method: str, path: str) -> dict[str, str]:
    handler = routes.get((method.upper(), path))

    if handler is None:
        return {"error": "Route not found"}

    return handler()


if __name__ == "__main__":
    print("Registered routes:", list(routes))
    print(handle_request("GET", "/health"))
    print(handle_request("GET", "/hello"))
    print(handle_request("GET", "/unknown"))
