from notes_backend.config import Settings
from notes_backend.embeddings import compute_embedding


def test_compute_embedding_uses_fallback_when_no_api_key():
    settings = Settings(openai_api_key=None)

    embedding = compute_embedding("bonjour", settings)

    assert len(embedding) == 256
    assert all(isinstance(v, float) for v in embedding)


def test_compute_embedding_fallback_is_deterministic():
    settings = Settings(openai_api_key=None)

    first = compute_embedding("même texte", settings)
    second = compute_embedding("même texte", settings)

    assert first == second


def test_compute_embedding_fallback_differs_for_different_texts():
    settings = Settings(openai_api_key=None)

    assert compute_embedding("texte A", settings) != compute_embedding("texte B", settings)
