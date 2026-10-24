from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PhotoUpdateRequest(BaseModel):
    description: str | None = Field(default=None, max_length=1000)


class PhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    description: str | None
    image_url: str
    owner_id: UUID
    created_at: datetime
    tags: list[str]


class TransformationKind(str, Enum):
    RESIZE = "resize"
    CROP = "crop"
    GRAYSCALE = "grayscale"
    BLUR = "blur"
    ROTATION = "rotation"


class TransformationRequest(BaseModel):
    kind: TransformationKind
    width: int | None = Field(default=None, ge=1, le=4000)
    height: int | None = Field(default=None, ge=1, le=4000)
    angle: int | None = Field(default=None, ge=0, le=359)


class TransformationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    kind: str
    image_url: str
    qr_code: str
    created_at: datetime
