"""Chat RAG-lite : récupère les notes les plus pertinentes puis génère une réponse contextuelle."""

from sqlmodel import Session

from notes_backend.config import Settings
from notes_backend.llm import complete
from notes_backend.services.search_service import search_notes

CHAT_SYSTEM_PROMPT = (
    "Tu es un assistant qui répond aux questions de l'utilisateur en te basant UNIQUEMENT "
    "sur ses notes personnelles fournies en contexte. Si l'information n'y figure pas, "
    "dis-le clairement. Réponds en français, de façon concise."
)


def chat_with_notes(session: Session, settings: Settings, message: str) -> tuple[str, list[str]]:
    results = search_notes(session, settings, message)
    if not results:
        return "Je n'ai trouvé aucune note pertinente pour répondre à cette question.", []

    context = "\n\n---\n\n".join(f"[{note.title}]\n{note.content}" for note, _ in results)
    prompt = f"Notes pertinentes :\n{context}\n\nQuestion : {message}"
    answer = complete(prompt, settings, system=CHAT_SYSTEM_PROMPT)
    source_ids = [note.id for note, _ in results]
    return answer, source_ids
