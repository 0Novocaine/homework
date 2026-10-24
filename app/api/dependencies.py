from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.integrations.cloudinary_service import CloudinaryService
from app.integrations.qr_service import QRCodeService
from app.models.user import Role, User
from app.repositories.comments import CommentRepository
from app.repositories.photos import PhotoRepository
from app.repositories.users import UserRepository
from app.services.auth import AuthService
from app.services.comments import CommentService
from app.services.photos import PhotoService
from app.services.users import UserService

bearer_scheme = HTTPBearer()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


def get_photo_service(db: Session = Depends(get_db)) -> PhotoService:
    return PhotoService(PhotoRepository(db), CloudinaryService(), QRCodeService())


def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    return CommentService(CommentRepository(db), PhotoRepository(db))


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)
) -> User:
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        if not subject:
            raise JWTError
        user = UserRepository(db).get_by_id(UUID(subject))
    except (JWTError, ValueError):
        user = None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user


def require_roles(*roles: Role) -> Callable:
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return dependency


require_moderator = require_roles(Role.MODERATOR, Role.ADMIN)
require_admin = require_roles(Role.ADMIN)
