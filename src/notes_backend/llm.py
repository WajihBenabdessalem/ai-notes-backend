"""Génération de texte (résumé, chat) via l'API OpenAI, avec repli déterministe si pas de clé."""

from notes_backend.config import Settings


def _fallback_completion(prompt: str) -> str:
    """Réponse de secours (tests / démo hors ligne) — n'est PAS un vrai résumé/chat généré."""
    return f"[réponse simulée — aucune clé API configurée] {prompt[:120]}"


def complete(prompt: str, settings: Settings, system: str | None = None) -> str:
    """Complète un prompt via le LLM configuré."""
    if not settings.openai_api_key:
        return _fallback_completion(prompt)

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content or ""
