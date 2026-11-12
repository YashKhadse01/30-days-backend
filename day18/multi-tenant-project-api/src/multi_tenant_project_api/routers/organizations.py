
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_tenant_project_api.database import get_db
from multi_tenant_project_api.models import (
    Membership,
    Organization,
    OrganizationRole,
    User,
)
from multi_tenant_project_api.routers.auth import get_current_user
from multi_tenant_project_api.schemas.organizations import (
    OrganizationCreate,
    OrganizationResponse,
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=201,
)
async def create_organization(
    payload: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an organization and assign its creator OWNER."""

    name = payload.name.strip()

    if len(name) < 2:
        raise HTTPException(
            status_code=422,
            detail="Organization name must contain at least 2 characters",
        )

    organization = Organization(
        name=name,
        created_by=current_user.id,
    )

    db.add(organization)
    await db.flush()

    membership = Membership(
        organization_id=organization.id,
        user_id=current_user.id,
        role=OrganizationRole.OWNER,
    )

    db.add(membership)
    await db.commit()
    await db.refresh(organization)

    return organization


@router.get(
    "",
    response_model=list[OrganizationResponse],
)
async def list_my_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return only organizations belonging to the user."""

    statement = (
        select(Organization)
        .join(
            Membership,
            Membership.organization_id == Organization.id,
        )
        .where(Membership.user_id == current_user.id)
    )

    result = await db.scalars(statement)

    return result.all()


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
async def get_organization(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Prevent access to organizations outside the user's tenant."""

    statement = (
        select(Organization)
        .join(
            Membership,
            Membership.organization_id == Organization.id,
        )
        .where(
            Organization.id == organization_id,
            Membership.user_id == current_user.id,
        )
    )

    organization = await db.scalar(statement)

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    return organization
