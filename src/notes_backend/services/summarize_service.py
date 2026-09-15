"""Génération de résumé pour une note existante."""

from sqlmodel import Session

from notes_backend.config import Settings
from notes_backend.llm import complete
from notes_backend.services.notes_service import get_note

SUMMARY_SYSTEM_PROMPT = (
    "Tu résumes des notes personnelles en 2 phrases maximum, en français, "
    "sans inventer d'information absente du texte."
)


def summarize_note(session: Session, settings: Settings, note_id: str) -> str:
    note = get_note(session, note_id)
    prompt = f"Titre : {note.title}\n\nContenu :\n{note.content}"
    return complete(prompt, settings, system=SUMMARY_SYSTEM_PROMPT)
