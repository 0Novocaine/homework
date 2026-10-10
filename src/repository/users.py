"""Database operations for user accounts and profiles."""

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user by email address.

    :param email: The email address of the user.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user if found, otherwise None.
    :rtype: User | None
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user and attempts to assign a Gravatar image.

    :param body: The data for the new user.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Stores or removes a user's refresh token.

    :param user: The user whose refresh token will be changed.
    :type user: User
    :param token: The new refresh token, or None to remove it.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Marks the user with the specified email address as confirmed.

    :param email: The email address to confirm.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: None.
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    if user is not None:
        user.confirmed = True
        db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User | None:
    """
    Updates the avatar URL of a user.

    :param email: The email address of the user.
    :type email: str
    :param url: The URL of the uploaded avatar.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: The updated user, or None when the user does not exist.
    :rtype: User | None
    """
    user = await get_user_by_email(email, db)
    if user is None:
        return None
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
