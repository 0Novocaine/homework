from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.photo import Photo, PhotoTransformation
from app.models.tag import Tag


class PhotoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, photo_id: UUID) -> Photo | None:
        return self.db.scalar(select(Photo).options(selectinload(Photo.tags)).where(Photo.id == photo_id))

    def add(self, photo: Photo) -> Photo:
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return photo

    def update(self, photo: Photo) -> Photo:
        self.db.commit()
        self.db.refresh(photo)
        return photo

    def delete(self, photo: Photo) -> None:
        self.db.delete(photo)
        self.db.commit()

    def list(self, search: str | None, tag: str | None, page: int, page_size: int, newest: bool) -> tuple[list[Photo], int]:
        statement = select(Photo).options(selectinload(Photo.tags))
        if search:
            statement = statement.where(Photo.description.ilike(f"%{search}%"))
        if tag:
            statement = statement.join(Photo.tags).where(Tag.name == tag.strip().lower())
        statement = statement.distinct()
        total = self.db.scalar(select(func.count()).select_from(statement.subquery())) or 0
        ordering = Photo.created_at.desc() if newest else Photo.created_at.asc()
        return list(self.db.scalars(statement.order_by(ordering).offset((page - 1) * page_size).limit(page_size))), total

    def list_by_owner(self, owner_id: UUID) -> list[Photo]:
        return list(self.db.scalars(select(Photo).where(Photo.owner_id == owner_id)))

    def get_or_create_tag(self, name: str) -> Tag:
        tag = self.db.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            try:
                with self.db.begin_nested():
                    tag = Tag(name=name)
                    self.db.add(tag)
                    self.db.flush()
            except IntegrityError:
                tag = self.db.scalar(select(Tag).where(Tag.name == name))
                if tag is None:
                    raise
        return tag

    def add_transformation(self, transformation: PhotoTransformation) -> PhotoTransformation:
        self.db.add(transformation)
        self.db.commit()
        self.db.refresh(transformation)
        return transformation
