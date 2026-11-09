
import os
import secrets
from urllib.parse import urlsplit

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from oauth_by_hand.account_linking import (
    login_or_register_google,
    users,
)
from oauth_by_hand.authorization import build_google_authorization_url
from oauth_by_hand.google_identity import verify_google_id_token
from oauth_by_hand.oauth_state import consume_oauth_context
from oauth_by_hand.sessions import (
    create_session,
    get_session_user_id,
    revoke_session,
)
from oauth_by_hand.token_exchange import exchange_google_code


load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://127.0.0.1:8000/auth/google/callback",
)

app = FastAPI(
    title="Day 15 - OAuth by Hand",
    description=(
        "Manual Google OAuth 2.0 authorization code flow "
        "with PKCE, state validation, and account linking"
    ),
    version="1.0.0",
)

bearer_scheme = HTTPBearer(auto_error=False)


# -------------------------
# Health endpoints
# -------------------------

@app.get("/")
def home():
    return {
        "message": "Day 15 OAuth API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "oauth-by-hand",
    }


# -------------------------
# Google OAuth login
# -------------------------

@app.get("/auth/google/login")
def google_login():
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=503,
            detail="Google OAuth client is not configured",
        )

    browser_binding = secrets.token_urlsafe(32)

    authorization_url, _state = build_google_authorization_url(
        client_id=GOOGLE_CLIENT_ID,
        redirect_uri=GOOGLE_REDIRECT_URI,
        browser_binding=browser_binding,
    )

    response = RedirectResponse(
        url=authorization_url,
        status_code=302,
    )

    response.set_cookie(
        key="oauth_browser_binding",
        value=browser_binding,
        httponly=True,
        secure=GOOGLE_REDIRECT_URI.startswith("https://"),
        samesite="lax",
        max_age=300,
        path="/auth/google",
    )

    return response


# -------------------------
# Google OAuth callback
# -------------------------

@app.get("/auth/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    """Complete Google OAuth authorization code flow."""

    def failure(status_code: int, detail: str):
        response = JSONResponse(
            status_code=status_code,
            content={"detail": detail},
        )
        response.delete_cookie(
            "oauth_browser_binding",
            path="/auth/google",
        )
        return response

    if error is not None:
        return failure(
            400,
            "Google authorization was not completed",
        )

    if not code or not state:
        return failure(
            400,
            "Missing OAuth callback parameters",
        )

    browser_binding = request.cookies.get(
        "oauth_browser_binding",
        "",
    )

    context = consume_oauth_context(
        state,
        browser_binding=browser_binding,
    )

    if context is None:
        return failure(
            401,
            "Invalid or expired OAuth state",
        )

    code_verifier, expected_nonce = context

    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")

    if not client_id:
        return failure(
            503,
            "Google OAuth is not configured",
        )

    try:
        tokens = await exchange_google_code(
            code=code,
            code_verifier=code_verifier,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=GOOGLE_REDIRECT_URI,
        )

        id_token = tokens.get("id_token")

        if not isinstance(id_token, str) or not id_token:
            return failure(
                401,
                "Missing Google ID token",
            )

        claims = await verify_google_id_token(
            id_token,
            client_id,
            expected_nonce=expected_nonce,
        )

        user = login_or_register_google(claims)
        session_token = create_session(user.user_id)

    except (httpx.HTTPError, ValueError, KeyError):
        return failure(
            401,
            "Google authentication failed",
        )

    response = JSONResponse(
        content={
            "message": "Google authentication successful",
            "user_id": user.user_id,
            "email": user.email,
            "provider": "google",
        },
    )

    response.set_cookie(
        key="app_session",
        value=session_token,
        httponly=True,
        secure=GOOGLE_REDIRECT_URI.startswith("https://"),
        samesite="lax",
        max_age=1800,
        path="/",
    )

    response.delete_cookie(
        "oauth_browser_binding",
        path="/auth/google",
    )

    return response


# -------------------------
# Authentication dependency
# -------------------------

def require_authenticated_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
):
    """Authenticate using a session cookie or Bearer token."""

    token = request.cookies.get("app_session")

    if not token and credentials is not None:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    user_id = get_session_user_id(token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session",
        )

    user = users.get(user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user


# -------------------------
# Authenticated profile
# -------------------------

@app.get("/auth/me")
def get_my_profile(
    user=Depends(require_authenticated_user),
):
    return {
        "user_id": user.user_id,
        "email": user.email,
        "google_linked": bool(user.google_subjects),
    }


# -------------------------
# Same-origin CSRF protection
# -------------------------

def require_same_origin(request: Request) -> None:
    """Reject cross-origin requests to sensitive endpoints."""

    expected_origin = (
        f"{request.url.scheme}://{request.url.netloc}"
    )

    origin = request.headers.get("origin")

    if origin is not None:
        if origin != expected_origin:
            raise HTTPException(
                status_code=403,
                detail="Cross-origin request rejected",
            )
        return

    referer = request.headers.get("referer")

    if referer is not None:
        parsed = urlsplit(referer)

        referer_origin = (
            f"{parsed.scheme}://{parsed.netloc}"
        )

        if referer_origin == expected_origin:
            return

    raise HTTPException(
        status_code=403,
        detail="Same-origin verification required",
    )


# -------------------------
# Logout
# -------------------------

@app.post("/auth/logout")
def logout_endpoint(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    user=Depends(require_authenticated_user),
):
    """Revoke the authenticated session."""

    cookie_token = request.cookies.get("app_session")

    bearer_token = (
        credentials.credentials
        if credentials is not None
        else None
    )

    # Cookie-based authentication requires same-origin verification.
    if cookie_token:
        require_same_origin(request)

    # Revoke the token selected by authentication.
    token = cookie_token or bearer_token

    if token:
        revoke_session(token)

    response = JSONResponse(
        content={
            "message": "Logged out successfully",
        }
    )

    response.delete_cookie(
        key="app_session",
        path="/",
    )

    return response
