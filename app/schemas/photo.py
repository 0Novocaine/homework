from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class PhotoPageResponse(BaseModel):
    items: list[PhotoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


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

    @model_validator(mode="after")
    def validate_options(self):
        if self.kind == TransformationKind.RESIZE and self.width is None and self.height is None:
            raise ValueError("Resize requires width or height")
        if self.kind == TransformationKind.CROP and (self.width is None or self.height is None):
            raise ValueError("Crop requires both width and height")
        if self.kind == TransformationKind.ROTATION and self.angle is None:
            raise ValueError("Rotation requires angle")
        if self.kind in {TransformationKind.GRAYSCALE, TransformationKind.BLUR} and any(
            value is not None for value in (self.width, self.height, self.angle)
        ):
            raise ValueError(f"{self.kind.value} does not accept dimensions or angle")
        if self.kind in {TransformationKind.RESIZE, TransformationKind.CROP} and self.angle is not None:
            raise ValueError(f"{self.kind.value} does not accept angle")
        if self.kind == TransformationKind.ROTATION and (self.width is not None or self.height is not None):
            raise ValueError("Rotation does not accept dimensions")
        return self


class TransformationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    kind: str
    image_url: str
    qr_code: str
    created_at: datetime
