"""Database operations for contacts owned by users."""

from datetime import date

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate


def get_contacts(skip: int, limit: int, user: User, db: Session) -> list[Contact]:
    """
    Retrieves contacts belonging to a specific user with pagination.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The owner of the contacts.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of the user's contacts.
    :rtype: list[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


def get_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Retrieves a contact by identifier when it belongs to a specific user.

    :param contact_id: The identifier of the contact.
    :type contact_id: int
    :param user: The owner of the contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact, or None when it does not exist or has another owner.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


def search_contacts(query: str, skip: int, limit: int, user: User, db: Session) -> list[Contact]:
    """
    Searches a user's contacts by first name, last name, or email address.

    :param query: The text to search for.
    :type query: str
    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The owner of the contacts.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Contacts matching the search query.
    :rtype: list[Contact]
    """
    pattern = f"%{query}%"
    return (
        db.query(Contact)
        .filter(
            Contact.user_id == user.id,
            or_(
                Contact.first_name.ilike(pattern),
                Contact.last_name.ilike(pattern),
                Contact.email.ilike(pattern),
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_contact(body: ContactCreate, user: User, db: Session) -> Contact:
    """
    Creates a contact for a specific user.

    :param body: The data for the new contact.
    :type body: ContactCreate
    :param user: The owner of the new contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(**body.model_dump(), user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
    """
    Updates a contact belonging to a specific user.

    :param contact_id: The identifier of the contact to update.
    :type contact_id: int
    :param body: The updated contact data.
    :type body: ContactUpdate
    :param user: The owner of the contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None when it does not exist.
    :rtype: Contact | None
    """
    contact = get_contact(contact_id, user, db)
    if contact is None:
        return None

    for field, value in body.model_dump().items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Deletes a contact belonging to a specific user.

    :param contact_id: The identifier of the contact to delete.
    :type contact_id: int
    :param user: The owner of the contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The deleted contact, or None when it does not exist.
    :rtype: Contact | None
    """
    contact = get_contact(contact_id, user, db)
    if contact is None:
        return None
    db.delete(contact)
    db.commit()
    return contact


def get_upcoming_birthdays(days: int, user: User, db: Session) -> list[Contact]:
    """
    Returns contacts whose next birthday falls within the requested period.

    :param days: The number of days from today to include.
    :type days: int
    :param user: The owner of the contacts.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Contacts with an upcoming birthday.
    :rtype: list[Contact]
    """
    today = date.today()
    end_date = today.fromordinal(today.toordinal() + days)
    contacts = db.query(Contact).filter(Contact.user_id == user.id).all()

    def next_birthday(birthday: date) -> date:
        try:
            occurrence = birthday.replace(year=today.year)
        except ValueError:  # February 29 in a non-leap year
            occurrence = birthday.replace(year=today.year, day=28)
        if occurrence < today:
            try:
                occurrence = birthday.replace(year=today.year + 1)
            except ValueError:
                occurrence = birthday.replace(year=today.year + 1, day=28)
        return occurrence

    return [contact for contact in contacts if today <= next_birthday(contact.birthday) <= end_date]
