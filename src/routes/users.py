import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas import UserDb
from src.services.auth import auth_service

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me/', response_model=UserDb)
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user),
):
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(
    file: UploadFile = File(..., description='Avatar image'),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    if not settings.cloudinary_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Cloudinary is not configured',
        )
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail='Only image files can be used as avatars',
        )

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    uploaded = cloudinary.uploader.upload(
        file.file,
        public_id=f'ContactsAPI/{current_user.username}',
        overwrite=True,
        resource_type='image',
    )
    avatar_url, _ = cloudinary.utils.cloudinary_url(
        uploaded['public_id'],
        version=uploaded['version'],
        width=250,
        height=250,
        crop='fill',
        secure=True,
    )
    user = await repository_users.update_avatar(current_user.email, avatar_url, db)
    return user
