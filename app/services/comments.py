from uuid import UUID

from fastapi import HTTPException

from app.models.comment import Comment
from app.models.user import Role, User
from app.repositories.comments import CommentRepository
from app.repositories.photos import PhotoRepository
from app.schemas.comment import CommentCreateRequest, CommentUpdateRequest


class CommentService:
    def __init__(self, comments: CommentRepository, photos: PhotoRepository):
        self.comments = comments
        self.photos = photos

    def create(self, photo_id: UUID, user: User, data: CommentCreateRequest) -> Comment:
        photo = self.photos.get(photo_id)
        if photo is None:
            raise HTTPException(status_code=404, detail="Photo not found")
        if photo.owner_id == user.id:
            raise HTTPException(status_code=403, detail="You cannot comment on your own photo")
        return self.comments.add(Comment(text=data.text, user_id=user.id, photo_id=photo_id))

    def list(self, photo_id: UUID) -> list[Comment]:
        if self.photos.get(photo_id) is None:
            raise HTTPException(status_code=404, detail="Photo not found")
        return self.comments.list_for_photo(photo_id)

    def update(self, photo_id: UUID, comment_id: UUID, user: User, data: CommentUpdateRequest) -> Comment:
        comment = self._get(comment_id)
        if comment.photo_id != photo_id:
            raise HTTPException(status_code=404, detail="Comment not found")
        if comment.user_id != user.id:
            raise HTTPException(status_code=403, detail="Only the author may edit this comment")
        comment.text = data.text
        return self.comments.update(comment)

    def delete(self, photo_id: UUID, comment_id: UUID, user: User) -> None:
        comment = self._get(comment_id)
        if comment.photo_id != photo_id:
            raise HTTPException(status_code=404, detail="Comment not found")
        if user.role not in {Role.ADMIN, Role.MODERATOR}:
            raise HTTPException(status_code=403, detail="Moderator role is required")
        self.comments.delete(comment)

    def _get(self, comment_id: UUID) -> Comment:
        comment = self.comments.get(comment_id)
        if comment is None:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment
