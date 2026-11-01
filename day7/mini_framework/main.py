from app import MiniApp, Request, Response

app = MiniApp()

todos: dict[int, dict[str, object]] = {}
next_id = 1

@app.get("/health")
def health(request: Request) -> Response:
    return Response({"status": "healthy"})

@app.get("/todos")
def list_todos(request: Request) -> Response:
    return Response({"todos": list(todos.values())})

@app.get("/todos/{todo_id}")
def get_todo(request: Request, todo_id: int) -> Response:
    todo = todos.get(todo_id)

    if todo is None:
        return Response(
            {"error": "Todo not found"},
            status_code=404,
        )

    return Response({"todo": todo})

@app.post("/todos")
def create_todo(request: Request) -> Response:
    global next_id

    data = request.json()
    if not isinstance(data, dict):
        return Response({"error": "JSON object required"}, 400)

    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return Response(
            {"error": "Valid title is required"},
            status_code=400,
        )

    todo = {
        "id": next_id,
        "title": title.strip(),
        "completed": False,
    }

    todos[next_id] = todo
    next_id += 1

    return Response({"todo": todo}, status_code=201)

@app.put("/todos/{todo_id}")
def update_todo(request: Request, todo_id: int) -> Response:
    todo = todos.get(todo_id)

    if todo is None:
        return Response({"error": "Todo not found"}, 404)

    data = request.json()

    if not isinstance(data, dict):
        return Response({"error": "JSON object required"}, 400)

    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            return Response({"error": "Invalid title"}, 400)
        todo["title"] = title.strip()

    if "completed" in data:
        completed = data["completed"]
        if not isinstance(completed, bool):
            return Response({"error": "Invalid completed value"}, 400)
        todo["completed"] = completed

    return Response({"todo": todo})

@app.delete("/todos/{todo_id}")
def delete_todo(request: Request, todo_id: int) -> Response:
    if todo_id not in todos:
        return Response({"error": "Todo not found"}, 404)

    del todos[todo_id]
    return Response({"message": "Todo deleted"})
