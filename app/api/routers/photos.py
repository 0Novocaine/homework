from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.api.dependencies import get_current_user, get_photo_service
from app.models.photo import Photo
from app.models.user import User
from app.schemas.photo import PhotoResponse, PhotoUpdateRequest, TransformationRequest, TransformationResponse
from app.services.photos import PhotoService

router = APIRouter(prefix="/photos", tags=["Photos"])


def photo_response(photo: Photo) -> PhotoResponse:
    return PhotoResponse(id=photo.id, description=photo.description, image_url=photo.image_url, owner_id=photo.owner_id,
                         created_at=photo.created_at, tags=[tag.name for tag in photo.tags])


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED, summary="Upload a photo")
async def create_photo(
    image: UploadFile = File(...), description: str | None = Form(default=None), tags: list[str] = Form(default=[]),
    user: User = Depends(get_current_user), service: PhotoService = Depends(get_photo_service),
):
    return photo_response(service.create(user, image, await image.read(), description, tags))


@router.get("/{photo_id}", response_model=PhotoResponse, summary="Get a photo by its unique URL")
def get_photo(photo_id: UUID, service: PhotoService = Depends(get_photo_service)):
    return photo_response(service.get(photo_id))


@router.patch("/{photo_id}", response_model=PhotoResponse, summary="Edit a photo description")
def update_photo(photo_id: UUID, data: PhotoUpdateRequest, user: User = Depends(get_current_user), service: PhotoService = Depends(get_photo_service)):
    return photo_response(service.update(photo_id, user, data))


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a photo")
def delete_photo(photo_id: UUID, user: User = Depends(get_current_user), service: PhotoService = Depends(get_photo_service)):
    service.delete(photo_id, user)


@router.post("/{photo_id}/transformations", response_model=TransformationResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a transformed image URL and QR code")
def transform_photo(photo_id: UUID, data: TransformationRequest, user: User = Depends(get_current_user), service: PhotoService = Depends(get_photo_service)):
    return service.transform(photo_id, user, data)
