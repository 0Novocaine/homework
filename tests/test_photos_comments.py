from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.orm import Session

from app.api.dependencies import get_photo_service
from app.integrations.qr_service import QRCodeService
from app.main import app
from app.repositories.photos import PhotoRepository
from app.services.photos import PhotoService
from tests.conftest import register, token


class FakeCloudinary:
    def upload(self, content: bytes, filename: str) -> tuple[str, str]:
        return "https://images.example/photo.jpg", "photoshare/photo"

    def delete(self, public_id: str) -> None:
        self.deleted = public_id

    def transformed_url(self, public_id: str, kind: str, width: int | None, height: int | None, angle: int | None):
        return f"https://images.example/{kind}.jpg", {"kind": kind}


def image_file() -> tuple[str, bytes, str]:
    buffer = BytesIO()
    Image.new("RGB", (10, 10), "blue").save(buffer, "PNG")
    return "photo.png", buffer.getvalue(), "image/png"


def use_fake_photo_service(db: Session) -> None:
    app.dependency_overrides[get_photo_service] = lambda: PhotoService(
        PhotoRepository(db), FakeCloudinary(), QRCodeService()
    )


def upload(client: TestClient, headers: dict[str, str], tags: list[str] | None = None):
    name, content, content_type = image_file()
    data = {"tags": tags} if tags else None
    return client.post("/api/photos", headers=headers, files={"image": (name, content, content_type)}, data=data)


def test_upload_get_edit_transform_and_delete_photo(client: TestClient, db: Session):
    use_fake_photo_service(db)
    register(client, "owner", "owner@example.com")
    headers = token(client, "owner")
    created = upload(client, headers, ["Nature", "City"])
    assert created.status_code == 201, created.text
    photo = created.json()
    assert set(photo["tags"]) == {"nature", "city"}
    photo_id = photo["id"]
    assert client.get(f"/api/photos/{photo_id}").status_code == 200
    assert client.patch(f"/api/photos/{photo_id}", json={"description": "edited"}, headers=headers).json()["description"] == "edited"
    transformed = client.post(f"/api/photos/{photo_id}/transformations", json={"kind": "grayscale"}, headers=headers)
    assert transformed.status_code == 201
    assert transformed.json()["qr_code"].startswith("data:image/png;base64,")
    assert client.delete(f"/api/photos/{photo_id}", headers=headers).status_code == 204


def test_photo_permissions_tags_and_upload_validation(client: TestClient, db: Session):
    use_fake_photo_service(db)
    register(client, "owner", "owner@example.com")
    register(client, "other", "other@example.com")
    owner_headers, other_headers = token(client, "owner"), token(client, "other")
    photo_id = upload(client, owner_headers).json()["id"]
    assert client.patch(f"/api/photos/{photo_id}", json={"description": "no"}, headers=other_headers).status_code == 403
    assert upload(client, owner_headers, ["a", "b", "c", "d", "e", "f"]).status_code == 422
    assert upload(client, owner_headers, ["same", "SAME"]).status_code == 422
    response = client.post("/api/photos", headers=owner_headers, files={"image": ("bad.txt", b"no", "text/plain")})
    assert response.status_code == 415


def test_comments_author_edit_and_moderator_deletion(client: TestClient, db: Session):
    use_fake_photo_service(db)
    register(client, "admin", "admin@example.com")
    register(client, "author", "author@example.com")
    register(client, "other", "other@example.com")
    photo_id = upload(client, token(client, "admin")).json()["id"]
    author_headers = token(client, "author")
    comment = client.post(f"/api/photos/{photo_id}/comments", json={"text": "hello"}, headers=author_headers).json()
    assert client.get(f"/api/photos/{photo_id}/comments").json()[0]["text"] == "hello"
    assert client.patch(f"/api/photos/{photo_id}/comments/{comment['id']}", json={"text": "changed"}, headers=author_headers).status_code == 200
    assert client.delete(f"/api/photos/{photo_id}/comments/{comment['id']}", headers=token(client, "other")).status_code == 403
    assert client.delete(f"/api/photos/{photo_id}/comments/{comment['id']}", headers=token(client, "admin")).status_code == 204
