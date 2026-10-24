from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import Role, User
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, data: RegisterRequest) -> User:
        if self.users.get_by_username(data.username):
            raise HTTPException(status_code=409, detail="Username is already in use")
        role = Role.ADMIN if self.users.count() == 0 else Role.USER
        user = User(username=data.username, email=str(data.email), first_name=data.first_name,
                    password_hash=hash_password(data.password), role=role)
        try:
            return self.users.add(user)
        except IntegrityError as exc:
            self.users.db.rollback()
            raise HTTPException(status_code=409, detail="Email is already in use") from exc

    def login(self, data: LoginRequest) -> str:
        user = self.users.get_by_username(data.username)
        if user is None or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        return create_access_token(str(user.id))
