import json
from urllib import request, error

BASE_URL = "http://127.0.0.1:8003"

def send_request(
    method: str,
    endpoint: str,
    data: dict | None = None,
) -> None:

    url = BASE_URL + endpoint

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")

    req = request.Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )

    try:
        with request.urlopen(req, timeout=5) as response:
            status = response.status
            result = json.loads(response.read())

    except error.HTTPError as exc:
        status = exc.code
        result = json.loads(exc.read())

    except error.URLError as exc:
        print(f"Connection failed: {exc.reason}")
        return

    print(f"\n{method} {endpoint}")
    print(f"HTTP Status: {status}")
    print(json.dumps(result, indent=4))


def main() -> None:
    print("=== Day 5 Raw HTTP API Testing ===")

    # Test 1: Check server health
    send_request("GET", "/health")

    # Test 2: Get all users
    send_request("GET", "/users")

    # Test 3: Create a new user
    send_request(
        "POST",
        "/users",
        {"name": "Charlie"},
    )

    # Test 4: Retrieve the created user
    send_request("GET", "/users/3")

    # Test 5: Request a nonexistent user
    send_request("GET", "/users/999")

    # Test 6: Test unsupported HTTP method
    send_request("DELETE", "/users")

if __name__ == "__main__":
    main()
