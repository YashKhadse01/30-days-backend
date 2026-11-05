from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic import BaseModel, Field
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_verified: bool
    created_at: datetime

class EmailVerificationRequest(BaseModel):
    token: str = Field(min_length=1, max_length=256)