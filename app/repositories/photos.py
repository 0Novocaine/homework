from uuid import UUID

from sqlalchemy import select
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

    def get_or_create_tag(self, name: str) -> Tag:
        tag = self.db.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag = Tag(name=name)
            self.db.add(tag)
            self.db.flush()
        return tag

    def add_transformation(self, transformation: PhotoTransformation) -> PhotoTransformation:
        self.db.add(transformation)
        self.db.commit()
        self.db.refresh(transformation)
        return transformation
