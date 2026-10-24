from abc import ABC, abstractmethod
from io import BytesIO

import cloudinary
import cloudinary.uploader
import cloudinary.utils

from app.core.config import get_settings


class TransformationStrategy(ABC):
    @abstractmethod
    def build(self, width: int | None, height: int | None, angle: int | None) -> dict: ...


class ResizeStrategy(TransformationStrategy):
    def build(self, width: int | None, height: int | None, angle: int | None) -> dict:
        return {"width": width, "height": height, "crop": "scale"}


class CropStrategy(TransformationStrategy):
    def build(self, width: int | None, height: int | None, angle: int | None) -> dict:
        return {"width": width, "height": height, "crop": "fill"}


class GrayscaleStrategy(TransformationStrategy):
    def build(self, width: int | None, height: int | None, angle: int | None) -> dict:
        return {"effect": "grayscale"}


class BlurStrategy(TransformationStrategy):
    def build(self, width: int | None, height: int | None, angle: int | None) -> dict:
        return {"effect": "blur:500"}


class RotationStrategy(TransformationStrategy):
    def build(self, width: int | None, height: int | None, angle: int | None) -> dict:
        return {"angle": angle or 90}


class CloudinaryService:
    _strategies = {
        "resize": ResizeStrategy(), "crop": CropStrategy(), "grayscale": GrayscaleStrategy(),
        "blur": BlurStrategy(), "rotation": RotationStrategy(),
    }

    def __init__(self) -> None:
        settings = get_settings()
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name, api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret, secure=True,
        )

    def upload(self, content: bytes, filename: str) -> tuple[str, str]:
        result = cloudinary.uploader.upload(BytesIO(content), folder="photoshare", public_id=filename.rsplit(".", 1)[0])
        return result["secure_url"], result["public_id"]

    def delete(self, public_id: str) -> None:
        cloudinary.uploader.destroy(public_id)

    def transformed_url(self, public_id: str, kind: str, width: int | None, height: int | None, angle: int | None) -> tuple[str, dict]:
        options = self._strategies[kind].build(width, height, angle)
        url, _ = cloudinary.utils.cloudinary_url(public_id, secure=True, **options)
        return url, options
