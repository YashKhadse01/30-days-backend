
from datetime import datetime

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)


class OrganizationResponse(BaseModel):
    id: str
    name: str
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MembershipResponse(BaseModel):
    id: str
    organization_id: str
    user_id: str
    role: str

    model_config = {"from_attributes": True}
