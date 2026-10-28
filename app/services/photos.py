import json
import logging
from io import BytesIO
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.integrations.cloudinary_service import CloudinaryService
from app.integrations.qr_service import QRCodeService
from app.models.photo import Photo, PhotoTransformation
from app.models.user import Role, User
from app.repositories.photos import PhotoRepository
from app.schemas.photo import PhotoUpdateRequest, TransformationRequest

logger = logging.getLogger(__name__)
_FORMAT_MIME = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


class PhotoService:
    def __init__(self, photos: PhotoRepository, cloudinary: CloudinaryService, qr_codes: QRCodeService):
        self.photos = photos
        self.cloudinary = cloudinary
        self.qr_codes = qr_codes

    @staticmethod
    def _normalize_tags(tags: list[str]) -> list[str]:
        normalized = [tag.strip().lower() for tag in tags if tag.strip()]
        if len(normalized) > 5:
            raise HTTPException(status_code=422, detail="A photo may have at most 5 tags")
        if len(set(normalized)) != len(normalized):
            raise HTTPException(status_code=422, detail="Tags must be unique")
        if any(len(tag) > 50 for tag in normalized):
            raise HTTPException(status_code=422, detail="A tag is too long")
        return normalized

    @staticmethod
    def _assert_owner_or_admin(photo: Photo, user: User) -> None:
        if photo.owner_id != user.id and user.role != Role.ADMIN:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    def get(self, photo_id: UUID) -> Photo:
        photo = self.photos.get(photo_id)
        if photo is None:
            raise HTTPException(status_code=404, detail="Photo not found")
        return photo

    def create(self, owner: User, upload: UploadFile, content: bytes, description: str | None, tags: list[str]) -> Photo:
        settings = get_settings()
        if upload.content_type not in settings.allowed_image_types:
            raise HTTPException(status_code=415, detail="Only JPEG, PNG, and WebP files are allowed")
        if len(content) > settings.max_upload_size_bytes:
            raise HTTPException(status_code=413, detail="Image exceeds 5 MB limit")
        try:
            image = Image.open(BytesIO(content))
            image_format = image.format
            image.verify()
        except (UnidentifiedImageError, OSError):
            raise HTTPException(status_code=422, detail="Uploaded file is not a valid image")
        if _FORMAT_MIME.get(image_format) != upload.content_type:
            raise HTTPException(status_code=422, detail="Image content does not match its MIME type")
        normalized_tags = self._normalize_tags(tags)
        try:
            image_url, public_id = self.cloudinary.upload(content, str(uuid4()))
        except Exception as exc:
            logger.exception("Cloudinary upload failed")
            raise HTTPException(status_code=502, detail="Could not upload image to storage") from exc
        try:
            photo = Photo(description=description, image_url=image_url, public_id=public_id, owner_id=owner.id)
            photo.tags = [self.photos.get_or_create_tag(tag) for tag in normalized_tags]
            return self.photos.add(photo)
        except SQLAlchemyError as exc:
            self.photos.db.rollback()
            try:
                self.cloudinary.delete(public_id)
            except Exception:
                logger.exception("Could not compensate failed photo creation")
            raise HTTPException(status_code=500, detail="Could not save photo") from exc

    def list(self, search: str | None, tag: str | None, page: int, page_size: int, sort: str) -> tuple[list[Photo], int]:
        return self.photos.list(search, tag, page, page_size, newest=sort == "newest")

    def update(self, photo_id: UUID, user: User, data: PhotoUpdateRequest) -> Photo:
        photo = self.get(photo_id)
        self._assert_owner_or_admin(photo, user)
        photo.description = data.description
        return self.photos.update(photo)

    def delete(self, photo_id: UUID, user: User) -> None:
        photo = self.get(photo_id)
        self._assert_owner_or_admin(photo, user)
        try:
            self.cloudinary.delete(photo.public_id)
        except Exception as exc:
            logger.exception("Cloudinary deletion failed for photo %s", photo.id)
            raise HTTPException(status_code=502, detail="Could not delete image from storage") from exc
        try:
            self.photos.delete(photo)
        except SQLAlchemyError as exc:
            self.photos.db.rollback()
            logger.exception("Database deletion failed after Cloudinary deletion for photo %s", photo.id)
            raise HTTPException(status_code=500, detail="Could not delete photo record") from exc

    def transform(self, photo_id: UUID, user: User, data: TransformationRequest) -> PhotoTransformation:
        photo = self.get(photo_id)
        self._assert_owner_or_admin(photo, user)
        image_url, options = self.cloudinary.transformed_url(
            photo.public_id, data.kind.value, data.width, data.height, data.angle
        )
        transformation = PhotoTransformation(
            photo_id=photo.id, kind=data.kind.value, options=json.dumps(options), image_url=image_url,
            qr_code=self.qr_codes.create_data_url(image_url),
        )
        return self.photos.add_transformation(transformation)
