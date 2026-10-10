"""HTTP routes for managing authenticated users' contacts."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas import ContactCreate, ContactResponse, ContactUpdate
from src.services.auth import auth_service
from src.services.rate_limit import CompatibleRateLimiter, user_identifier

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"],
    dependencies=[
        Depends(
            CompatibleRateLimiter(
                times=10,
                seconds=60,
                identifier=user_identifier,
            )
        )
    ],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/",
    response_model=list[ContactResponse],
    summary="Get all contacts",
    description="No more than 10 requests per minute.",
)
def read_contacts(db: DbSession, current_user: User = Depends(auth_service.get_current_user), skip: int = 0, limit: int = Query(default=100, le=100)):
    """
    Returns a paginated list of contacts owned by the authenticated user.

    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :return: A list of contacts.
    :rtype: list[ContactResponse]
    """
    return repository_contacts.get_contacts(skip, limit, current_user, db)


@router.get("/search/", response_model=list[ContactResponse], summary="Search contacts")
def search_contacts(
    db: DbSession,
    current_user: User = Depends(auth_service.get_current_user),
    query: str = Query(min_length=1, description="Part of first name, last name, or email"),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
):
    """
    Searches contacts owned by the authenticated user.

    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :param query: Text contained in a contact's name or email.
    :type query: str
    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :return: Contacts matching the query.
    :rtype: list[ContactResponse]
    """
    return repository_contacts.search_contacts(query, skip, limit, current_user, db)


@router.get("/upcoming-birthdays/", response_model=list[ContactResponse], summary="Get birthdays in the next 7 days")
def read_upcoming_birthdays(db: DbSession, current_user: User = Depends(auth_service.get_current_user)):
    """
    Returns the authenticated user's contacts with birthdays in the next seven days.

    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: Contacts with an upcoming birthday.
    :rtype: list[ContactResponse]
    """
    return repository_contacts.get_upcoming_birthdays(days=7, user=current_user, db=db)


@router.get("/{contact_id}", response_model=ContactResponse, summary="Get a contact")
def read_contact(contact_id: int, db: DbSession, current_user: User = Depends(auth_service.get_current_user)):
    """
    Returns a contact by identifier when it belongs to the authenticated user.

    :param contact_id: The identifier of the requested contact.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The requested contact.
    :rtype: ContactResponse
    :raises HTTPException: If the contact does not exist or has another owner.
    """
    contact = repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, summary="Create a contact")
def create_contact(body: ContactCreate, db: DbSession, current_user: User = Depends(auth_service.get_current_user)):
    """
    Creates a contact for the authenticated user.

    :param body: The data for the new contact.
    :type body: ContactCreate
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The newly created contact.
    :rtype: ContactResponse
    :raises HTTPException: If a duplicate contact causes a database integrity error.
    """
    try:
        return repository_contacts.create_contact(body, current_user, db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A contact with this email already exists")


@router.put("/{contact_id}", response_model=ContactResponse, summary="Update a contact")
def update_contact(contact_id: int, body: ContactUpdate, db: DbSession, current_user: User = Depends(auth_service.get_current_user)):
    """
    Updates a contact belonging to the authenticated user.

    :param contact_id: The identifier of the contact to update.
    :type contact_id: int
    :param body: The updated contact data.
    :type body: ContactUpdate
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The updated contact.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is absent or an integrity error occurs.
    """
    try:
        contact = repository_contacts.update_contact(contact_id, body, current_user, db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A contact with this email already exists")
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse, summary="Delete a contact")
def remove_contact(contact_id: int, db: DbSession, current_user: User = Depends(auth_service.get_current_user)):
    """
    Deletes a contact belonging to the authenticated user.

    :param contact_id: The identifier of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The deleted contact.
    :rtype: ContactResponse
    :raises HTTPException: If the contact does not exist or has another owner.
    """
    contact = repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
