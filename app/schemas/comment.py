from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CommentCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class CommentUpdateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    text: str
    user_id: UUID
    photo_id: UUID
    created_at: datetime
    updated_at: datetime
