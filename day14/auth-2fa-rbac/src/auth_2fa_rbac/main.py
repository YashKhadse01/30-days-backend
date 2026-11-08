
import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from pydantic import BaseModel, Field

from auth_2fa_rbac.auth_service import (
    begin_login,
    complete_login,
    create_user,
    get_session_user,
    logout as revoke_session,
)
from auth_2fa_rbac.totp import generate_totp_secret
from auth_2fa_rbac.rbac import (
    Permission,
    has_permission,
)


# ----------------------------------
# FastAPI Application
# ----------------------------------

app = FastAPI(
    title="Day 14 - 2FA + RBAC API",
    description=(
        "Authentication with Argon2id, "
        "TOTP, backup codes and RBAC"
    ),
    version="1.0.0",
)


# ----------------------------------
# Request Models
# ----------------------------------

class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class Verify2FARequest(BaseModel):
    challenge_token: str = Field(min_length=1)
    otp: str = Field(min_length=1)


# ----------------------------------
# Authentication Dependency
# Define BEFORE protected endpoints
# ----------------------------------

bearer_scheme = HTTPBearer(auto_error=False)


def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_session_user(
        credentials.credentials
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def require_role_permission(permission: Permission):
    """Check whether the authenticated user has permission."""

    def check_permission(
        user=Depends(require_authenticated_user),
    ):
        if not has_permission(user.role, permission):
            raise HTTPException(
                status_code=403,
                detail="Access denied: insufficient permissions",
            )

        return user

    return check_permission



# ----------------------------------
# Health Endpoints
# ----------------------------------

@app.get("/")
def home():
    return {
        "message": "Day 14 Authentication API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "auth-2fa-rbac",
    }


# ----------------------------------
# Step 1: Password Authentication
# ----------------------------------

@app.post("/auth/login")
def login(data: LoginRequest):
    challenge = begin_login(
        data.username,
        data.password,
    )

    if challenge is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "message": "Password verified. 2FA required.",
        "challenge_token": challenge,
        "expires_in": 300,
    }


# ----------------------------------
# Step 2: Two-Factor Authentication
# ----------------------------------

@app.post("/auth/verify-2fa")
def verify_2fa(data: Verify2FARequest):
    session_token = complete_login(
        challenge_token=data.challenge_token,
        otp=data.otp,
    )

    if session_token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired 2FA verification",
        )

    return {
        "message": "Two-factor authentication successful",
        "session_token": session_token,
        "token_type": "Bearer",
        "expires_in": 1800,
    }


# ----------------------------------
# Step 3: Authenticated Profile
# ----------------------------------

@app.get("/auth/me")
def get_my_profile(
    user=Depends(require_authenticated_user),
):
    return {
        "username": user.username,
        "role": user.role,
        "two_factor_authenticated": True,
    }


# ----------------------------------
# Step 4: Secure Logout
# ----------------------------------

@app.post("/auth/logout")
def logout_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    user=Depends(require_authenticated_user),
):
    revoke_session(
        credentials.credentials
    )

    return {
        "message": "Logged out successfully",
    }

# ----------------------------------
# RBAC-Protected Endpoints
# ----------------------------------

@app.get("/reports")
def read_reports(
    user=Depends(
        require_role_permission(Permission.REPORTS_READ)
    ),
):
    return {
        "message": "Reports retrieved successfully",
        "reports": [
            {"id": 1, "title": "Monthly Performance"},
            {"id": 2, "title": "Security Audit"},
        ],
        "accessed_by": user.username,
    }


@app.post("/reports")
def create_report(
    user=Depends(
        require_role_permission(Permission.REPORTS_CREATE)
    ),
):
    return {
        "message": "Report creation permitted",
        "created_by": user.username,
    }


@app.get("/admin/users")
def manage_users(
    user=Depends(
        require_role_permission(Permission.USERS_MANAGE)
    ),
):
    return {
        "message": "User management access granted",
        "admin": user.username,
    }


# ----------------------------------
# Development Demo Account
# ----------------------------------

# NEVER enable demo mode in production.

if os.getenv("DAY14_DEMO_MODE") == "1":

    secret_file = Path(".totp_test_secret")

    if secret_file.exists():
        demo_secret = secret_file.read_text(
            encoding="utf-8"
        ).strip()

    else:
        demo_secret = generate_totp_secret()

        secret_file.write_text(
            demo_secret,
            encoding="utf-8",
        )

    create_user(
        username="testuser",
        password="StrongPassword123!",
        role="user",
        totp_secret=demo_secret,
    )
