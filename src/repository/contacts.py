from datetime import date

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate


def get_contacts(skip: int, limit: int, user: User, db: Session) -> list[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


def get_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


def search_contacts(query: str, skip: int, limit: int, user: User, db: Session) -> list[Contact]:
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
    contact = Contact(**body.model_dump(), user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
    contact = get_contact(contact_id, user, db)
    if contact is None:
        return None

    for field, value in body.model_dump().items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    contact = get_contact(contact_id, user, db)
    if contact is None:
        return None
    db.delete(contact)
    db.commit()
    return contact


def get_upcoming_birthdays(days: int, user: User, db: Session) -> list[Contact]:
    """Return contacts whose next birthday is between today and today + days."""
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
