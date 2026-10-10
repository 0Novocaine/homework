"""Database operations for notes owned by users."""

from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Note, Tag, User
from src.schemas import NoteModel, NoteUpdate, NoteStatusUpdate


async def get_notes(skip: int, limit: int, user: User, db: Session) -> List[Note]:
    """
    Retrieves notes belonging to a specific user with pagination.

    :param skip: The number of notes to skip.
    :type skip: int
    :param limit: The maximum number of notes to return.
    :type limit: int
    :param user: The owner of the notes.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of the user's notes.
    :rtype: List[Note]
    """
    return db.query(Note).filter(Note.user_id == user.id).offset(skip).limit(limit).all()


async def get_note(note_id: int, user: User, db: Session) -> Note:
    """
    Retrieves a note by its identifier for a specific user.

    :param note_id: The identifier of the note.
    :type note_id: int
    :param user: The owner of the note.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The note if it exists and belongs to the user, otherwise None.
    :rtype: Note | None
    """
    return db.query(Note).filter(and_(Note.id == note_id, Note.user_id == user.id)).first()


async def create_note(body: NoteModel, user: User, db: Session) -> Note:
    """
    Creates a note and assigns the user's selected tags to it.

    :param body: The data for the new note.
    :type body: NoteModel
    :param user: The owner of the new note.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created note.
    :rtype: Note
    """
    tags = db.query(Tag).filter(and_(Tag.id.in_(body.tags), Tag.user_id == user.id)).all()
    note = Note(title=body.title, description=body.description, tags=tags, user=user)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


async def remove_note(note_id: int, user: User, db: Session) -> Note | None:
    """
    Deletes a note belonging to a specific user.

    :param note_id: The identifier of the note to delete.
    :type note_id: int
    :param user: The owner of the note.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The deleted note, or None when it does not exist.
    :rtype: Note | None
    """
    note = db.query(Note).filter(and_(Note.id == note_id, Note.user_id == user.id)).first()
    if note:
        db.delete(note)
        db.commit()
    return note


async def update_note(note_id: int, body: NoteUpdate, user: User, db: Session) -> Note | None:
    """
    Updates a note and its tag associations for a specific user.

    :param note_id: The identifier of the note to update.
    :type note_id: int
    :param body: The updated note data.
    :type body: NoteUpdate
    :param user: The owner of the note.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated note, or None when it does not exist.
    :rtype: Note | None
    """
    note = db.query(Note).filter(and_(Note.id == note_id, Note.user_id == user.id)).first()
    if note:
        tags = db.query(Tag).filter(and_(Tag.id.in_(body.tags), Tag.user_id == user.id)).all()
        note.title = body.title
        note.description = body.description
        note.done = body.done
        note.tags = tags
        db.commit()
    return note


async def update_status_note(note_id: int, body: NoteStatusUpdate, user: User, db: Session) -> Note | None:
    """
    Updates the completion status of a user's note.

    :param note_id: The identifier of the note to update.
    :type note_id: int
    :param body: The new completion status.
    :type body: NoteStatusUpdate
    :param user: The owner of the note.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated note, or None when it does not exist.
    :rtype: Note | None
    """
    note = db.query(Note).filter(and_(Note.id == note_id, Note.user_id == user.id)).first()
    if note:
        note.done = body.done
        db.commit()
    return note
