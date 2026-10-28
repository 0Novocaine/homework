from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_user_service, require_admin
from app.models.user import User
from app.schemas.user import PublicProfileResponse, UserResponse, UserRoleUpdate, UserStatusUpdate, UserUpdateRequest
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, summary="Get own profile")
def get_me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserResponse, summary="Update own profile")
def update_me(data: UserUpdateRequest, user: User = Depends(get_current_user), service: UserService = Depends(get_user_service)):
    return service.update_me(user, data)


@router.get("/{username}", response_model=PublicProfileResponse, summary="Get a public user profile")
def public_profile(username: str, service: UserService = Depends(get_user_service)):
    user, photo_count = service.public_profile(username)
    return PublicProfileResponse(username=user.username, first_name=user.first_name, created_at=user.created_at, photo_count=photo_count)


@router.patch("/{username}/active", response_model=UserResponse, summary="Ban or unban a user")
def set_active(username: str, data: UserStatusUpdate, _: User = Depends(require_admin), service: UserService = Depends(get_user_service)):
    admin = _
    target, _photo_count = service.public_profile(username)
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot change your own active status")
    return service.set_active(target, data.is_active)


@router.patch("/{username}/role", response_model=UserResponse, summary="Change a user role between USER and MODERATOR")
def change_role(username: str, data: UserRoleUpdate, admin: User = Depends(require_admin), service: UserService = Depends(get_user_service)):
    target, _photo_count = service.public_profile(username)
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot change your own role")
    return service.change_role(target, data.role)


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user and their data")
def delete_user(username: str, admin: User = Depends(require_admin), service: UserService = Depends(get_user_service)):
    target, _photo_count = service.public_profile(username)
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")
    service.delete(target)
