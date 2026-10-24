from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, comment_id: UUID) -> Comment | None:
        return self.db.get(Comment, comment_id)

    def list_for_photo(self, photo_id: UUID) -> list[Comment]:
        return list(self.db.scalars(select(Comment).where(Comment.photo_id == photo_id).order_by(Comment.created_at)))

    def add(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def update(self, comment: Comment) -> Comment:
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
        self.db.commit()
