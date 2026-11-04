from itertools import count

_task_counter = count(1)

def make_task_payload(
    *,
    title: str | None = None,
    description: str | None = None,
) -> dict:
    """Generate valid task creation payloads for API tests."""
    number = next(_task_counter)

    return {
        "title": title if title is not None else f"Test Task {number}",
        "description": description,
    }
