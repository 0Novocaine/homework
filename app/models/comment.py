import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.photo import Photo
    from app.models.user import User


class Comment(TimestampMixin, Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    photo_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("photos.id", ondelete="CASCADE"), index=True, nullable=False)

    author: Mapped["User"] = relationship(back_populates="comments")
    photo: Mapped["Photo"] = relationship(back_populates="comments")
