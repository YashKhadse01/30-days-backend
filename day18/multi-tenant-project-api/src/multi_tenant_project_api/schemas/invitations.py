
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class InvitationRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class InvitationCreate(BaseModel):
    email: EmailStr
    role: InvitationRole = InvitationRole.MEMBER


class InvitationAccept(BaseModel):
    token: str = Field(min_length=1)


class InvitationResponse(BaseModel):
    id: str
    organization_id: str
    email: EmailStr
    role: InvitationRole
    expires_at: datetime
    accepted_at: datetime | None = None


class InvitationCreatedResponse(InvitationResponse):
    # Development only. In production, deliver the
    # invitation token through a secure email channel.
    invitation_token: str
