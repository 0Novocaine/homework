from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas import ContactCreate, ContactResponse, ContactUpdate
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[ContactResponse], summary="Get all contacts")
def read_contacts(db: DbSession, current_user: User = Depends(auth_service.get_current_user), skip: int = 0, limit: int = Query(default=100, le=100)):
    return repository_contacts.get_contacts(skip, limit, current_user, db)


@router.get("/search/", response_model=list[ContactResponse], summary="Search contacts")
def search_contacts(
    db: DbSession,
    current_user: User = Depends(auth_service.get_current_user),
    query: str = Query(min_length=1, description="Part of first name, last name, or email"),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
):
    return repository_contacts.search_contacts(query, skip, limit, current_user, db)


@router.get("/upcoming-birthdays/", response_model=list[ContactResponse], summary="Get birthdays in the next 7 days")
def read_upcoming_birthdays(db: DbSession, current_user: User = Depends(auth_service.get_current_user)):
    return repository_contacts.get_upcoming_birthdays(days=7, user=current_user, db=db)


@router.get("/{contact_id}", response_model=ContactResponse, summary="Get a contact")
def read_contact(contact_id: int, db: DbSession, current_user: User = Depends(auth_service.get_current_user)):
    contact = repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, summary="Create a contact")
def create_contact(body: ContactCreate, db: DbSession, current_user: User = Depends(auth_service.get_current_user)):
    try:
        return repository_contacts.create_contact(body, current_user, db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A contact with this email already exists")


@router.put("/{contact_id}", response_model=ContactResponse, summary="Update a contact")
def update_contact(contact_id: int, body: ContactUpdate, db: DbSession, current_user: User = Depends(auth_service.get_current_user)):
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
    contact = repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
