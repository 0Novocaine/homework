from fastapi import HTTPException

from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.user import UserUpdateRequest


class UserService:
    def __init__(self, users: UserRepository):
        self.users = users

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
        user.is_active = is_active
        return self.users.update(user)
