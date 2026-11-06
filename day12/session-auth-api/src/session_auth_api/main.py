from session_auth_api.auth import get_current_user
from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from session_auth_api.csrf import validate_request_origin
from session_auth_api.csrf import require_csrf
from session_auth_api.database import settings
from session_auth_api.models import Session
from session_auth_api.schemas import UserLogin, MessageResponse
from session_auth_api.security import verify_password
from session_auth_api.sessions import (
    generate_session_token,
    hash_session_token,
    get_session_expiry,
)

from session_auth_api.database import get_db
from session_auth_api.models import User
from session_auth_api.schemas import UserRegister, UserResponse
from session_auth_api.security import hash_password
from datetime import datetime, timezone
from session_auth_api.auth import get_current_session
ALLOWED_ORIGINS = {
    "http://127.0.0.1:8000",
    "http://localhost:8000",
}

app = FastAPI(
    title="Day 12 - Session Authentication API",
    version="0.1.0",
)
from session_auth_api.csrf import (
    CSRF_COOKIE_NAME,
    generate_csrf_token,
)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    email = str(data.email).lower()

    # Check whether this email is already registered.
    result = await db.execute(
        select(User).where(User.email == email)
    )

    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail="Unable to register with these details",
        )

    # Hash the password before database storage.
    user = User(
        email=email,
        password_hash=hash_password(data.password),
        is_verified=False,
    )

    db.add(user)

    try:
        await db.commit()

    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Unable to register with these details",
        ) from exc

    await db.refresh(user)

    return user

@app.post("/auth/login", response_model=MessageResponse)
async def login(
    data: UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    
    # Reject login requests from untrusted browser origins.
    validate_request_origin(
        request=request,
        allowed_origins=ALLOWED_ORIGINS,
    )

    # An existing authenticated session must supply
    # a valid CSRF token before it can be rotated.
    existing_token = request.cookies.get(
        settings.session_cookie_name
    )

    if existing_token:
        result = await db.execute(
            select(Session).where(
                Session.token_hash == hash_session_token(
                    existing_token
                ),
                Session.revoked_at.is_(None),
                Session.expires_at > datetime.now(timezone.utc),
            )
        )

        existing_session = result.scalar_one_or_none()

        if existing_session is not None:
            require_csrf(
                request=request,
                session_token=existing_token,
                secret_key=settings.csrf_secret_key,
            )

    email = str(data.email).lower()

    result = await db.execute(
        select(User).where(User.email == email)
    )

    user = result.scalar_one_or_none()

    # Generic error prevents revealing whether an email exists.
    if user is None or not verify_password(
        data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )
    
    # Rotate an existing authenticated session on login.
    old_token = request.cookies.get(settings.session_cookie_name)

    if old_token:
        old_hash = hash_session_token(old_token)

        # Revoke only the presented session if it belongs
        # to the account that has just authenticated.
        await db.execute(
            update(Session)
            .where(
                Session.token_hash == old_hash,
                Session.user_id == user.id,
                Session.revoked_at.is_(None),
            )
            .values(
                revoked_at=datetime.now(timezone.utc)
            )
        )

    # Always issue a new, unpredictable session token.
    raw_token = generate_session_token()


    session = Session(
        user_id=user.id,
        token_hash=hash_session_token(raw_token),
        expires_at=get_session_expiry(),
    )

    db.add(session)
    await db.commit()

    # Development uses HTTP on localhost.
    # Production requires HTTPS and Secure=True.
    is_production = settings.app_env == "production"

    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=settings.session_expire_hours * 3600,
        path="/",
    )
    
    # Generate a signed CSRF token for this session.
    csrf_token = generate_csrf_token(
        session_token=raw_token,
        secret_key=settings.csrf_secret_key,
    )

    # CSRF cookie is readable by frontend JavaScript.
    # The session cookie remains HttpOnly.
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        secure=is_production,
        samesite="lax",
        max_age=settings.session_expire_hours * 3600,
        path="/",
    )


    return {"message": "Login successful"}

@app.get("/auth/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@app.post("/auth/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    response: Response,
    session: Session = Depends(get_current_session),
    db: AsyncSession = Depends(get_db),
):
    # Read the current session cookie.
    raw_token = request.cookies.get(
        settings.session_cookie_name
    )

    # Reject requests without valid CSRF protection.
    require_csrf(
        request=request,
        session_token=raw_token,
        secret_key=settings.csrf_secret_key,
    )
    validate_request_origin(
        request=request,
        allowed_origins=ALLOWED_ORIGINS,
    )

    # Revoke the current session.
    session.revoked_at = datetime.now(timezone.utc)
    await db.commit()

    # Clear the authentication cookie.
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        secure=settings.app_env == "production",
        httponly=True,
        samesite="lax",
    )

    # Clear the CSRF cookie.
    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/",
        secure=settings.app_env == "production",
        httponly=False,
        samesite="lax",
    )

    return {"message": "Logged out successfully"}



@app.post(
    "/auth/logout-all",
    response_model=MessageResponse,
)
async def logout_all(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    raw_token = request.cookies.get(
        settings.session_cookie_name
    )

    # Validate CSRF before changing any sessions.
    require_csrf(
        request=request,
        session_token=raw_token,
        secret_key=settings.csrf_secret_key,
    )
    validate_request_origin(
        request=request,
        allowed_origins=ALLOWED_ORIGINS,
    )

    # Revoke all active sessions for this user.
    await db.execute(
        update(Session)
        .where(
            Session.user_id == current_user.id,
            Session.revoked_at.is_(None),
        )
        .values(
            revoked_at=datetime.now(timezone.utc)
        )
    )

    await db.commit()

    # Remove both cookies from this browser.
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        secure=settings.app_env == "production",
        httponly=True,
        samesite="lax",
    )

    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/",
        secure=settings.app_env == "production",
        httponly=False,
        samesite="lax",
    )

    return {
        "message": "Logged out from all devices successfully"
    }
