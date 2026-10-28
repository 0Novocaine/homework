from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "olena_photo",
                "email": "olena@example.com",
                "password": "SecurePass123",
                "first_name": "Олена",
            }
        }
    )

    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    first_name: str | None = Field(default=None, max_length=100)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"username": "olena_photo", "password": "SecurePass123"}})

    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
