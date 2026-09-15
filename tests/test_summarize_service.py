import pytest

from notes_backend.services.notes_service import NoteNotFoundError, create_note
from notes_backend.services.summarize_service import summarize_note


def test_summarize_note_returns_fallback_text_when_no_api_key(session, settings):
    note = create_note(session, settings, title="Titre", content="Contenu à résumer")

    summary = summarize_note(session, settings, note.id)

    assert "réponse simulée" in summary


def test_summarize_note_raises_when_note_missing(session, settings):
    with pytest.raises(NoteNotFoundError):
        summarize_note(session, settings, "id-inexistant")
