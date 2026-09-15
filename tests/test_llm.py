from notes_backend.config import Settings
from notes_backend.llm import complete


def test_complete_uses_fallback_when_no_api_key():
    settings = Settings(openai_api_key=None)

    result = complete("Résume ce texte.", settings)

    assert "réponse simulée" in result
