import time

import pytest

from notes_backend.services.notes_service import (
    NoteNotFoundError,
    create_note,
    delete_note,
    get_note,
    list_notes,
)


def test_create_note_persists_and_computes_embedding(session, settings):
    note = create_note(session, settings, title="Titre", content="Contenu")

    assert note.id
    assert note.title == "Titre"
    assert note.get_embedding()


def test_list_notes_returns_created_notes_most_recent_first(session, settings):
    create_note(session, settings, title="Première", content="A")
    time.sleep(0.01)
    create_note(session, settings, title="Deuxième", content="B")

    notes = list_notes(session)

    assert [n.title for n in notes] == ["Deuxième", "Première"]


def test_get_note_raises_when_not_found(session, settings):
    with pytest.raises(NoteNotFoundError):
        get_note(session, "id-inexistant")


def test_delete_note_removes_it(session, settings):
    note = create_note(session, settings, title="À supprimer", content="X")

    delete_note(session, note.id)

    assert list_notes(session) == []
