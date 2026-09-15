from notes_backend.services.notes_service import create_note
from notes_backend.services.search_service import search_notes


def test_search_notes_returns_empty_list_when_no_notes(session, settings):
    assert search_notes(session, settings, "question") == []


def test_search_notes_finds_matching_note_by_identical_text(session, settings):
    note = create_note(session, settings, title="Congés", content="Politique de congés payés")
    create_note(session, settings, title="Architecture", content="Micro-services et Kubernetes")

    # Le fallback (hash déterministe) n'a pas de vraie sémantique : on interroge donc avec le
    # même texte que celui indexé pour valider mécaniquement la chaîne embedding -> similarité
    # -> classement. Avec une vraie clé OpenAI, une requête reformulée fonctionnerait aussi.
    results = search_notes(session, settings, "Congés\nPolitique de congés payés")

    assert results
    assert results[0][0].id == note.id


def test_search_notes_excludes_unrelated_note_from_top_result(session, settings):
    create_note(session, settings, title="Congés", content="Politique de congés payés")
    unrelated = create_note(session, settings, title="Architecture", content="Kubernetes")

    results = search_notes(session, settings, "Congés\nPolitique de congés payés")

    assert results[0][0].id != unrelated.id
