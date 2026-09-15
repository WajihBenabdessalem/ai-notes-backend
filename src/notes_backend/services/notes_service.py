"""Opérations CRUD sur les notes, avec calcul et persistance de l'embedding à la création."""

from sqlmodel import Session, select

from notes_backend.config import Settings
from notes_backend.embeddings import compute_embedding
from notes_backend.models import Note


class NoteNotFoundError(LookupError):
    """Levée lorsqu'aucune note ne correspond à l'identifiant demandé."""


def create_note(session: Session, settings: Settings, title: str, content: str) -> Note:
    embedding = compute_embedding(f"{title}\n{content}", settings)
    note = Note(title=title, content=content)
    note.set_embedding(embedding)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note


def list_notes(session: Session) -> list[Note]:
    return list(session.exec(select(Note).order_by(Note.created_at.desc())))


def get_note(session: Session, note_id: str) -> Note:
    note = session.get(Note, note_id)
    if note is None:
        raise NoteNotFoundError(f"Note introuvable : {note_id}")
    return note


def delete_note(session: Session, note_id: str) -> None:
    note = get_note(session, note_id)
    session.delete(note)
    session.commit()
