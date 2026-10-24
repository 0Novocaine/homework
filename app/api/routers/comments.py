from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_comment_service, get_current_user
from app.models.user import User
from app.schemas.comment import CommentCreateRequest, CommentResponse, CommentUpdateRequest
from app.services.comments import CommentService

router = APIRouter(prefix="/photos/{photo_id}/comments", tags=["Comments"])


@router.get("", response_model=list[CommentResponse], summary="List comments under a photo")
def list_comments(photo_id: UUID, service: CommentService = Depends(get_comment_service)):
    return service.list(photo_id)


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED, summary="Comment on a photo")
def create_comment(photo_id: UUID, data: CommentCreateRequest, user: User = Depends(get_current_user), service: CommentService = Depends(get_comment_service)):
    return service.create(photo_id, user, data)


@router.patch("/{comment_id}", response_model=CommentResponse, summary="Edit own comment")
def update_comment(photo_id: UUID, comment_id: UUID, data: CommentUpdateRequest, user: User = Depends(get_current_user), service: CommentService = Depends(get_comment_service)):
    return service.update(photo_id, comment_id, user, data)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a comment as moderator or administrator")
def delete_comment(photo_id: UUID, comment_id: UUID, user: User = Depends(get_current_user), service: CommentService = Depends(get_comment_service)):
    service.delete(photo_id, comment_id, user)
