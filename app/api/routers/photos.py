from uuid import UUID

from math import ceil

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.api.dependencies import get_current_user, get_photo_service
from app.models.photo import Photo
from app.models.user import User
from app.core.config import get_settings
from app.schemas.photo import PhotoPageResponse, PhotoResponse, PhotoUpdateRequest, TransformationRequest, TransformationResponse
from app.services.photos import PhotoService

router = APIRouter(prefix="/photos", tags=["Photos"])


def photo_response(photo: Photo) -> PhotoResponse:
    return PhotoResponse(id=photo.id, description=photo.description, image_url=photo.image_url, owner_id=photo.owner_id,
                         created_at=photo.created_at, tags=[tag.name for tag in photo.tags])


async def read_image_limited(upload: UploadFile) -> bytes:
    limit = get_settings().max_upload_size_bytes
    chunks: list[bytes] = []
    total = 0
    while chunk := await upload.read(1024 * 1024):
        total += len(chunk)
        if total > limit:
            raise HTTPException(status_code=413, detail="Image exceeds 5 MB limit")
        chunks.append(chunk)
    return b"".join(chunks)


@router.get("", response_model=PhotoPageResponse, summary="Search and list photos")
def list_photos(
    search: str | None = Query(default=None, max_length=100),
    tag: str | None = Query(default=None, max_length=50),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="newest", pattern="^(newest|oldest)$"),
    service: PhotoService = Depends(get_photo_service),
):
    items, total = service.list(search, tag, page, page_size, sort)
    return PhotoPageResponse(items=[photo_response(photo) for photo in items], total=total, page=page,
                             page_size=page_size, total_pages=ceil(total / page_size) if total else 0)


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED, summary="Upload a photo")
async def create_photo(
    image: UploadFile = File(...), description: str | None = Form(default=None, max_length=1000), tags: list[str] = Form(default=[]),
    user: User = Depends(get_current_user), service: PhotoService = Depends(get_photo_service),
):
    return photo_response(service.create(user, image, await read_image_limited(image), description, tags))


@router.get("/{photo_id}", response_model=PhotoResponse, summary="Get a photo by its unique URL")
def get_photo(photo_id: UUID, service: PhotoService = Depends(get_photo_service)):
    return photo_response(service.get(photo_id))


@router.patch("/{photo_id}", response_model=PhotoResponse, summary="Edit a photo description")
@router.put("/{photo_id}", response_model=PhotoResponse, summary="Replace a photo description")
def update_photo(photo_id: UUID, data: PhotoUpdateRequest, user: User = Depends(get_current_user), service: PhotoService = Depends(get_photo_service)):
    return photo_response(service.update(photo_id, user, data))


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a photo")
def delete_photo(photo_id: UUID, user: User = Depends(get_current_user), service: PhotoService = Depends(get_photo_service)):
    service.delete(photo_id, user)


@router.post("/{photo_id}/transformations", response_model=TransformationResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a transformed image URL and QR code")
def transform_photo(photo_id: UUID, data: TransformationRequest, user: User = Depends(get_current_user), service: PhotoService = Depends(get_photo_service)):
    return service.transform(photo_id, user, data)
