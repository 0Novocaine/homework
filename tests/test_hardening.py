from io import BytesIO
from uuid import uuid4

import pytest
from fastapi import HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from app.models.photo import Photo
from app.models.comment import Comment
from app.models.user import Role, User
from app.repositories.photos import PhotoRepository
from app.repositories.comments import CommentRepository
from app.repositories.users import UserRepository
from app.schemas.photo import TransformationRequest
from app.services.photos import PhotoService
from app.services.users import UserService
from app.services.comments import CommentService
from app.schemas.comment import CommentCreateRequest, CommentUpdateRequest
from app.integrations.cloudinary_service import CloudinaryService


class FakeCloud:
    def __init__(self):
        self.deleted: list[str] = []

    def upload(self, _content, public_id):
        return "https://example.test/image.png", f"photoshare/{public_id}"

    def delete(self, public_id):
        self.deleted.append(public_id)

    def transformed_url(self, _public_id, kind, width, height, angle):
        return "https://example.test/transformed", {"kind": kind, "width": width, "height": height, "angle": angle}


class FakeQR:
    def create_data_url(self, _url):
        return "data:image/png;base64,test"


def image_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (2, 2)).save(buffer, "PNG")
    return buffer.getvalue()


@pytest.mark.parametrize("payload", [
    {"kind": "resize"}, {"kind": "crop", "width": 10}, {"kind": "rotation"},
    {"kind": "grayscale", "width": 10}, {"kind": "blur", "angle": 10},
])
def test_invalid_transformation_options(payload):
    with pytest.raises(ValueError):
        TransformationRequest.model_validate(payload)


def test_photo_service_uses_unique_id_and_rejects_mismatched_mime(db: Session):
    owner = User(username="owner", email="owner@example.com", password_hash="x", role=Role.USER)
    UserRepository(db).add(owner)
    cloud = FakeCloud()
    service = PhotoService(PhotoRepository(db), cloud, FakeQR())
    upload = UploadFile(filename="same-name.png", file=BytesIO(image_bytes()), headers={"content-type": "image/png"})
    photo = service.create(owner, upload, image_bytes(), None, [])
    assert photo.public_id.startswith("photoshare/")
    assert "same-name" not in photo.public_id
    bad = UploadFile(filename="wrong.jpg", file=BytesIO(image_bytes()), headers={"content-type": "image/jpeg"})
    with pytest.raises(HTTPException) as exc:
        service.create(owner, bad, image_bytes(), None, [])
    assert exc.value.status_code == 422
    transformation = service.transform(photo.id, owner, TransformationRequest(kind="rotation", angle=90))
    assert transformation.kind == "rotation"


def test_photo_delete_storage_failure_is_reported(db: Session):
    owner = UserRepository(db).add(User(username="owner3", email="owner3@example.com", password_hash="x", role=Role.USER))
    photo = PhotoRepository(db).add(Photo(description=None, image_url="https://x", public_id="delete-fail", owner_id=owner.id))
    cloud = FakeCloud()
    cloud.delete = lambda _public_id: (_ for _ in ()).throw(RuntimeError("storage unavailable"))
    with pytest.raises(HTTPException) as exc:
        PhotoService(PhotoRepository(db), cloud, FakeQR()).delete(photo.id, owner)
    assert exc.value.status_code == 502


def test_user_service_blocks_last_admin_and_deletes_owned_cloudinary_images(db: Session):
    users = UserRepository(db)
    admin = users.add(User(username="admin", email="admin@example.com", password_hash="x", role=Role.ADMIN))
    member = users.add(User(username="member", email="member@example.com", password_hash="x", role=Role.USER))
    cloud = FakeCloud()
    photos = PhotoRepository(db)
    photos.add(Photo(description=None, image_url="https://example.test/a", public_id="image-a", owner_id=member.id))
    service = UserService(users, photos, cloud)
    with pytest.raises(HTTPException):
        service.set_active(admin, False)
    service.delete(member)
    assert cloud.deleted == ["image-a"]
    assert users.get_by_id(member.id) is None


def test_cloudinary_service_strategies_and_client_calls(monkeypatch):
    service = CloudinaryService()
    monkeypatch.setattr("cloudinary.uploader.upload", lambda *_args, **_kwargs: {"secure_url": "https://x", "public_id": "p"})
    monkeypatch.setattr("cloudinary.uploader.destroy", lambda *_args, **_kwargs: {"result": "ok"})
    monkeypatch.setattr("cloudinary.utils.cloudinary_url", lambda *_args, **_kwargs: ("https://x/transformed", {}))
    assert service.upload(b"image", "uuid") == ("https://x", "p")
    service.delete("p")
    for kind, kwargs in [
        ("resize", {"width": 10, "height": None, "angle": None}),
        ("crop", {"width": 10, "height": 20, "angle": None}),
        ("grayscale", {"width": None, "height": None, "angle": None}),
        ("blur", {"width": None, "height": None, "angle": None}),
        ("rotation", {"width": None, "height": None, "angle": 90}),
    ]:
        url, options = service.transformed_url("p", kind, **kwargs)
        assert url.startswith("https://") and options


def test_comment_service_rejects_owner_and_enforces_author(db: Session):
    users = UserRepository(db)
    owner = users.add(User(username="owner2", email="owner2@example.com", password_hash="x", role=Role.USER))
    stranger = users.add(User(username="stranger", email="stranger@example.com", password_hash="x", role=Role.USER))
    photo = PhotoRepository(db).add(Photo(description=None, image_url="https://x", public_id="comment-photo", owner_id=owner.id))
    service = CommentService(CommentRepository(db), PhotoRepository(db))
    with pytest.raises(HTTPException):
        service.create(photo.id, owner, CommentCreateRequest(text="own"))
    comment = service.create(photo.id, stranger, CommentCreateRequest(text="hello"))
    with pytest.raises(HTTPException):
        service.update(photo.id, comment.id, owner, CommentUpdateRequest(text="no"))
    with pytest.raises(HTTPException):
        service.delete(photo.id, comment.id, stranger)
    assert service.list(photo.id)[0].id == comment.id
    with pytest.raises(HTTPException):
        service.list(uuid4())
