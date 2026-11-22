"""Real-time WebSocket endpoint."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket) -> None:
    """Echo incoming text messages until the client disconnects."""
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_json(
                {"event": "message", "data": message}
            )
    except WebSocketDisconnect:
        return
