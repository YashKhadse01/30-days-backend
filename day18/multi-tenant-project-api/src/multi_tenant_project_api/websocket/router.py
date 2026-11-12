
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from multi_tenant_project_api.config import settings
from multi_tenant_project_api.database import AsyncSessionLocal
from multi_tenant_project_api.models import Membership, User
from multi_tenant_project_api.routers.auth import (
    decode_access_token,
)
from multi_tenant_project_api.websocket.manager import (
    connection_manager,
)

router = APIRouter(tags=["WebSocket Notifications"])


@router.websocket("/ws/organizations/{organization_id}")
async def organization_notifications(
    websocket: WebSocket,
    organization_id: str,
):
    # Require a bearer token in the WebSocket handshake.
    # Non-browser clients can supply Authorization directly.
    authorization = websocket.headers.get(
        "authorization", ""
    )

    scheme, separator, token = authorization.partition(" ")

    if (
        not separator
        or scheme.lower() != "bearer"
        or not token.strip()
    ):
        await websocket.close(code=1008)
        return

    user_id = decode_access_token(
        token.strip(),
        settings.jwt_secret,
    )

    if user_id is None:
        await websocket.close(code=1008)
        return

    # Verify the user and organization membership.
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)

        if user is None:
            await websocket.close(code=1008)
            return

        membership = await db.scalar(
            select(Membership).where(
                Membership.organization_id == organization_id,
                Membership.user_id == user_id,
            )
        )

        if membership is None:
            await websocket.close(code=1008)
            return

    # Only authorized organization members reach this point.
    await connection_manager.connect(
        organization_id,
        websocket,
    )

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "organization_id": organization_id,
                "message": "Real-time notifications connected",
            }
        )

        while True:
            # Keep the connection open and detect disconnections.
            await websocket.receive_text()

    except WebSocketDisconnect:
        pass

    finally:
        await connection_manager.disconnect(
            organization_id,
            websocket,
        )
