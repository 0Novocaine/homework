from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import Role


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: EmailStr
    first_name: str | None
    role: Role
    is_active: bool
    created_at: datetime


class PublicProfileResponse(BaseModel):
    username: str
    first_name: str | None
    created_at: datetime
    photo_count: int


class UserUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserRoleUpdate(BaseModel):
    role: Role
