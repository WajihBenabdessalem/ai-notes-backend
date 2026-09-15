"""Recherche sémantique sur l'ensemble des notes, via similarité cosinus sur les embeddings."""

from sqlmodel import Session

from notes_backend.config import Settings
from notes_backend.embeddings import compute_embedding
from notes_backend.models import Note
from notes_backend.services.notes_service import list_notes
from notes_backend.similarity import rank_by_similarity


def search_notes(session: Session, settings: Settings, query: str) -> list[tuple[Note, float]]:
    notes = list_notes(session)
    if not notes:
        return []

    query_embedding = compute_embedding(query, settings)
    candidates = [(note.id, note.get_embedding()) for note in notes]
    ranked = rank_by_similarity(query_embedding, candidates, settings.top_k)

    notes_by_id = {note.id: note for note in notes}
    return [(notes_by_id[note_id], score) for note_id, score in ranked if score > 0]
