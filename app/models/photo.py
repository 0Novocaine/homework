import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.tag import Tag
    from app.models.user import User


photo_tags = Table(
    "photo_tags",
    Base.metadata,
    Column("photo_id", ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Photo(TimestampMixin, Base):
    __tablename__ = "photos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    description: Mapped[str | None] = mapped_column(String(1000))
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    public_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    owner: Mapped["User"] = relationship(back_populates="photos")
    tags: Mapped[list["Tag"]] = relationship(secondary=photo_tags, back_populates="photos")
    comments: Mapped[list["Comment"]] = relationship(back_populates="photo", cascade="all, delete-orphan")
    transformations: Mapped[list["PhotoTransformation"]] = relationship(
        back_populates="photo", cascade="all, delete-orphan"
    )


class PhotoTransformation(TimestampMixin, Base):
    __tablename__ = "photo_transformations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    photo_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("photos.id", ondelete="CASCADE"), index=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    options: Mapped[str] = mapped_column(String(500), nullable=False, default="{}")
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    qr_code: Mapped[str] = mapped_column(String(2048), nullable=False)

    photo: Mapped["Photo"] = relationship(back_populates="transformations")
