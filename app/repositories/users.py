from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.photo import Photo
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def count(self) -> int:
        return self.db.scalar(select(func.count()).select_from(User)) or 0

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)

    def add(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def photo_count(self, user_id: UUID) -> int:
        return self.db.scalar(select(func.count()).select_from(Photo).where(Photo.owner_id == user_id)) or 0
