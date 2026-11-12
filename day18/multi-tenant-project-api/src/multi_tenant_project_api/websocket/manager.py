
import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """Manage active WebSocket connections by organization."""

    def __init__(self):
        self.connections: dict[str, set[WebSocket]] = (
            defaultdict(set)
        )
        self._lock = asyncio.Lock()

    async def connect(
        self,
        organization_id: str,
        websocket: WebSocket,
    ):
        await websocket.accept()

        async with self._lock:
            self.connections[organization_id].add(websocket)

    async def disconnect(
        self,
        organization_id: str,
        websocket: WebSocket,
    ):
        async with self._lock:
            connections = self.connections.get(organization_id)

            if connections is None:
                return

            connections.discard(websocket)

            if not connections:
                self.connections.pop(organization_id, None)

    async def broadcast(
        self,
        organization_id: str,
        event: dict,
    ):
        async with self._lock:
            connections = list(
                self.connections.get(organization_id, set())
            )

        for websocket in connections:
            try:
                await websocket.send_json(event)
            except (RuntimeError, OSError):
                await self.disconnect(
                    organization_id,
                    websocket,
                )


connection_manager = ConnectionManager()
