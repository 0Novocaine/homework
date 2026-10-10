"""HTTP routes for managing authenticated users' notes."""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import NoteModel, NoteUpdate, NoteStatusUpdate, NoteResponse
from src.repository import notes as repository_notes
from src.services.auth import auth_service


router = APIRouter(prefix='/notes', tags=["notes"])




@router.get("/", response_model=List[NoteResponse])
async def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Returns a paginated list of notes owned by the authenticated user.

    :param skip: The number of notes to skip.
    :type skip: int
    :param limit: The maximum number of notes to return.
    :type limit: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: A list of notes.
    :rtype: List[NoteResponse]
    """
    notes = await repository_notes.get_notes(skip, limit, current_user, db)
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(note_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    """
    Returns a note by identifier when it belongs to the authenticated user.

    :param note_id: The identifier of the requested note.
    :type note_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The requested note.
    :rtype: NoteResponse
    :raises HTTPException: If the note does not exist or belongs to another user.
    """
    note = await repository_notes.get_note(note_id, current_user, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(body: NoteModel, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    Creates a note for the authenticated user.

    :param body: The data for the new note.
    :type body: NoteModel
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The newly created note.
    :rtype: NoteResponse
    """
    return await repository_notes.create_note(body, current_user, db)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(body: NoteUpdate, note_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    Updates a note owned by the authenticated user.

    :param body: The updated note data.
    :type body: NoteUpdate
    :param note_id: The identifier of the note to update.
    :type note_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The updated note.
    :rtype: NoteResponse
    :raises HTTPException: If the note does not exist or belongs to another user.
    """
    note = await repository_notes.update_note(note_id, body, current_user, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_status_note(body: NoteStatusUpdate, note_id: int, db: Session = Depends(get_db),
                             current_user: User = Depends(auth_service.get_current_user)):
    """
    Updates the completion status of a note owned by the authenticated user.

    :param body: The new completion status.
    :type body: NoteStatusUpdate
    :param note_id: The identifier of the note to update.
    :type note_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The updated note.
    :rtype: NoteResponse
    :raises HTTPException: If the note does not exist or belongs to another user.
    """
    note = await repository_notes.update_status_note(note_id, body, current_user, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.delete("/{note_id}", response_model=NoteResponse)
async def remove_note(note_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    Deletes a note owned by the authenticated user.

    :param note_id: The identifier of the note to delete.
    :type note_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The deleted note.
    :rtype: NoteResponse
    :raises HTTPException: If the note does not exist or belongs to another user.
    """
    note = await repository_notes.remove_note(note_id, current_user, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note
