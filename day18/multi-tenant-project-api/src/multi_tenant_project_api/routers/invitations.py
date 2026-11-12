
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from multi_tenant_project_api.database import get_db
from multi_tenant_project_api.models import (
    Invitation,
    Membership,
    Organization,
    OrganizationRole,
    User,
)
from multi_tenant_project_api.routers.auth import get_current_user
from multi_tenant_project_api.schemas.invitations import (
    InvitationAccept,
    InvitationCreate,
)
from multi_tenant_project_api.services.invitations import (
    generate_invitation_token,
    hash_invitation_token,
    invitation_expiration,
    is_invitation_expired,
)


router = APIRouter(tags=["Invitations"])


@router.post(
    "/organizations/{organization_id}/invitations",
    status_code=201,
)
async def create_invitation(
    organization_id: str,
    payload: InvitationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allow owners and admins to invite users."""

    membership = await db.scalar(
        select(Membership).where(
            Membership.organization_id == organization_id,
            Membership.user_id == current_user.id,
        )
    )

    if membership is None or membership.role not in (
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
    ):
        raise HTTPException(
            status_code=403,
            detail="Owner or admin permission required",
        )

    email = str(payload.email).strip().lower()

    existing_user = await db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        existing_membership = await db.scalar(
            select(Membership).where(
                Membership.organization_id == organization_id,
                Membership.user_id == existing_user.id,
            )
        )

        if existing_membership is not None:
            raise HTTPException(
                status_code=409,
                detail="User is already a member",
            )

    token, token_hash = generate_invitation_token()

    invitation = Invitation(
        organization_id=organization_id,
        email=email,
        role=OrganizationRole(payload.role.value),
        token_hash=token_hash,
        expires_at=invitation_expiration(),
        created_by=current_user.id,
    )

    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)

    # Development only: production should send the token
    # privately by email, never return it in the API response.
    return {
        "id": invitation.id,
        "organization_id": invitation.organization_id,
        "email": invitation.email,
        "role": invitation.role.value,
        "expires_at": invitation.expires_at,
        "invitation_token": token,
    }


@router.post("/invitations/accept")
async def accept_invitation(
    payload: InvitationAccept,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept a valid invitation exactly once."""

    token_hash = hash_invitation_token(payload.token)

    # Atomically claim the token so concurrent requests
    # cannot accept the same invitation twice.
    claimed = await db.execute(
        update(Invitation)
        .where(
            Invitation.token_hash == token_hash,
            Invitation.accepted_at.is_(None),
            Invitation.expires_at > datetime.now(timezone.utc),
            Invitation.email == current_user.email.lower(),
        )
        .values(accepted_at=datetime.now(timezone.utc))
        .returning(
            Invitation.organization_id,
            Invitation.role,
        )
    )

    row = claimed.one_or_none()

    if row is None:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid, expired, or already used invitation",
        )

    organization_id, role = row

    existing = await db.scalar(
        select(Membership).where(
            Membership.organization_id == organization_id,
            Membership.user_id == current_user.id,
        )
    )

    if existing is not None:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="User is already a member",
        )

    membership = Membership(
        organization_id=organization_id,
        user_id=current_user.id,
        role=role,
    )

    db.add(membership)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Membership already exists",
        )

    return {
        "message": "Invitation accepted",
        "organization_id": organization_id,
        "role": role.value,
    }
