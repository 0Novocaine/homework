import logging

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import Role, User
from app.repositories.photos import PhotoRepository
from app.repositories.users import UserRepository
from app.schemas.user import UserUpdateRequest

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, users: UserRepository, photos: PhotoRepository | None = None, cloudinary=None):
        self.users = users
        self.photos = photos
        self.cloudinary = cloudinary

    def public_profile(self, username: str) -> tuple[User, int]:
        user = self.users.get_by_username(username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user, self.users.photo_count(user.id)

    def update_me(self, user: User, data: UserUpdateRequest) -> User:
        if data.first_name is not None:
            user.first_name = data.first_name
        return self.users.update(user)

    def set_active(self, user: User, is_active: bool) -> User:
        if not is_active and user.role == Role.ADMIN and self.users.active_admin_count(excluding_id=user.id) == 0:
            raise HTTPException(status_code=400, detail="The last active administrator cannot be blocked")
        user.is_active = is_active
        return self.users.update(user)

    def change_role(self, user: User, role: Role) -> User:
        if user.role == Role.ADMIN or role == Role.ADMIN:
            raise HTTPException(status_code=422, detail="This endpoint only changes roles between USER and MODERATOR")
        user.role = role
        return self.users.update(user)

    def delete(self, user: User) -> None:
        if user.role == Role.ADMIN and user.is_active and self.users.active_admin_count(excluding_id=user.id) == 0:
            raise HTTPException(status_code=400, detail="The last active administrator cannot be deleted")
        if self.photos is None or self.cloudinary is None:
            raise RuntimeError("Photo storage dependencies are unavailable")
        for photo in self.photos.list_by_owner(user.id):
            try:
                self.cloudinary.delete(photo.public_id)
            except Exception as exc:
                raise HTTPException(status_code=502, detail="Could not delete a user image from storage") from exc
        try:
            self.users.delete(user)
        except SQLAlchemyError as exc:
            self.users.db.rollback()
            logger.exception("Database deletion failed for user %s", user.id)
            raise HTTPException(status_code=500, detail="Could not delete user record") from exc
