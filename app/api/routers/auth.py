from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_auth_service
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register a user")
def register(data: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    return service.register(data)


@router.post("/login", response_model=TokenResponse, summary="Get a JWT access token")
def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)):
    return TokenResponse(access_token=service.login(data))
