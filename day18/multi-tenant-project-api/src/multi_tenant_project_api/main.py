
from fastapi import FastAPI

from multi_tenant_project_api.routers.auth import (
    router as auth_router,
)
from multi_tenant_project_api.routers.organizations import (
    router as organizations_router,
)
from multi_tenant_project_api.routers.invitations import (
    router as invitations_router,
)
from multi_tenant_project_api.routers.tasks import (
    router as tasks_router,
)
from multi_tenant_project_api.websocket.router import (
    router as websocket_router,
)


app = FastAPI(
    title="Day 18 - Multi-Tenant Project Management API",
    description=(
        "Organizations, invitations, role-based access, "
        "task management, and real-time notifications."
    ),
    version="1.0.0",
)


app.router.include_router(auth_router)
app.router.include_router(organizations_router)
app.router.include_router(invitations_router)
app.router.include_router(tasks_router)
app.router.include_router(websocket_router)


@app.get("/")
async def home():
    return {
        "message": "Day 18 Project Management API",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "multi-tenant-project-api",
    }
