from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    database_url: str = Field(validation_alias='DATABASE_URL')
    jwt_secret_key: str = Field(validation_alias='JWT_SECRET_KEY', min_length=32)
    jwt_algorithm: str = Field(default='HS256', validation_alias='JWT_ALGORITHM')

    mail_username: str = Field(default='', validation_alias='MAIL_USERNAME')
    mail_password: str = Field(default='', validation_alias='MAIL_PASSWORD')
    mail_from: str = Field(default='', validation_alias='MAIL_FROM')
    mail_port: int = Field(default=465, validation_alias='MAIL_PORT')
    mail_server: str = Field(default='', validation_alias='MAIL_SERVER')

    redis_host: str = Field(default='localhost', validation_alias='REDIS_HOST')
    redis_port: int = Field(default=6379, validation_alias='REDIS_PORT')
    cors_origins: str = Field(
        default='http://localhost:3000', validation_alias='CORS_ORIGINS'
    )

    cloudinary_name: str = Field(default='', validation_alias='CLOUDINARY_NAME')
    cloudinary_api_key: str = Field(default='', validation_alias='CLOUDINARY_API_KEY')
    cloudinary_api_secret: str = Field(
        default='', validation_alias='CLOUDINARY_API_SECRET'
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]

    @property
    def cloudinary_configured(self) -> bool:
        return bool(
            self.cloudinary_name
            and self.cloudinary_api_key
            and self.cloudinary_api_secret
        )


settings = Settings()
