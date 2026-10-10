"""Database operations for tags owned by users."""

from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Tag, User
from src.schemas import TagModel


async def get_tags(skip: int, limit: int, user: User, db: Session) -> List[Tag]:
    """
    Retrieves tags belonging to a specific user with pagination.

    :param skip: The number of tags to skip.
    :type skip: int
    :param limit: The maximum number of tags to return.
    :type limit: int
    :param user: The owner of the tags.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of the user's tags.
    :rtype: List[Tag]
    """
    return db.query(Tag).filter(Tag.user_id == user.id).offset(skip).limit(limit).all()


async def get_tag(tag_id: int, user: User, db: Session) -> Tag:
    """
    Retrieves a tag by its identifier for a specific user.

    :param tag_id: The identifier of the tag.
    :type tag_id: int
    :param user: The owner of the tag.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The tag if it exists and belongs to the user, otherwise None.
    :rtype: Tag | None
    """
    return db.query(Tag).filter(and_(Tag.id == tag_id, Tag.user_id == user.id)).first()


async def create_tag(body: TagModel, user: User, db: Session) -> Tag:
    """
    Creates a tag for a specific user.

    :param body: The data for the new tag.
    :type body: TagModel
    :param user: The owner of the new tag.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created tag.
    :rtype: Tag
    """
    tag = Tag(name=body.name, user_id=user.id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def update_tag(tag_id: int, body: TagModel, user: User, db: Session) -> Tag | None:
    """
    Updates a tag belonging to a specific user.

    :param tag_id: The identifier of the tag to update.
    :type tag_id: int
    :param body: The updated tag data.
    :type body: TagModel
    :param user: The owner of the tag.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated tag, or None when it does not exist.
    :rtype: Tag | None
    """
    tag = db.query(Tag).filter(and_(Tag.id == tag_id, Tag.user_id == user.id)).first()
    if tag:
        tag.name = body.name
        db.commit()
        db.refresh(tag)
    return tag


async def remove_tag(tag_id: int, user: User, db: Session) -> Tag | None:
    """
    Deletes a tag belonging to a specific user.

    :param tag_id: The identifier of the tag to delete.
    :type tag_id: int
    :param user: The owner of the tag.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The deleted tag, or None when it does not exist.
    :rtype: Tag | None
    """
    tag = db.query(Tag).filter(and_(Tag.id == tag_id, Tag.user_id == user.id)).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag
