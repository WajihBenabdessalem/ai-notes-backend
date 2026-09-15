from notes_backend.services.chat_service import chat_with_notes
from notes_backend.services.notes_service import create_note


def test_chat_with_notes_returns_no_source_message_when_no_notes(session, settings):
    answer, sources = chat_with_notes(session, settings, "Bonjour")

    assert sources == []
    assert "aucune note" in answer.lower()


def test_chat_with_notes_uses_matching_note_as_context(session, settings):
    note = create_note(session, settings, title="Congés", content="25 jours de congés par an")

    answer, sources = chat_with_notes(session, settings, "Congés\n25 jours de congés par an")

    assert sources == [note.id]
    assert "réponse simulée" in answer
