from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from capstone_core.api.auth import router as auth_router
from capstone_core.api.google_oauth import router as google_oauth_router
from capstone_core.api.public_api import router as public_api_router
from capstone_core.api.two_factor import router as two_factor_router
from capstone_core.api.websocket import router as websocket_router
from capstone_core.core.config import get_settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Capstone Core API",
        description="Day 29 - Advanced Backend Capstone",
        version="0.1.0",
    )

    settings = get_settings()

    if settings.oauth_session_secret:
        if len(settings.oauth_session_secret) < 32:
            raise ValueError(
                "OAuth session secret must contain at least 32 characters"
            )

        app.add_middleware(
            SessionMiddleware,
            secret_key=settings.oauth_session_secret,
            session_cookie="capstone_oauth_session",
            same_site="lax",
            https_only=not settings.google_redirect_uri.startswith(
                "http://127.0.0.1:"
            ),
            max_age=600,
        )

    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    app.include_router(auth_router)
    app.include_router(google_oauth_router)
    app.include_router(two_factor_router)
    app.include_router(websocket_router)
    app.include_router(public_api_router)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    return app


app = create_app()
