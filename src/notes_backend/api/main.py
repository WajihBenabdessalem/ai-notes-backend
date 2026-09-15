"""Point d'entrée FastAPI : CRUD de notes + fonctionnalités IA (résumé, recherche, chat).

Ce backend est conçu pour être consommé par l'application iOS AINotesApp, développée dans le
dépôt compagnon `ai-notes-ios` (Swift Package AINotesKit + vues SwiftUI AINotesApp).
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from notes_backend.api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    NoteCreate,
    NoteRead,
    SearchRequest,
    SearchResultItem,
    SummarizeResponse,
)
from notes_backend.config import get_settings
from notes_backend.db import get_session, init_db
from notes_backend.services.chat_service import chat_with_notes
from notes_backend.services.notes_service import (
    NoteNotFoundError,
    create_note,
    delete_note,
    get_note,
    list_notes,
)
from notes_backend.services.search_service import search_notes
from notes_backend.services.summarize_service import summarize_note


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Notes Backend",
    description="Backend IA (résumé, recherche sémantique, chat) pour une app de notes iOS.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _to_read(note) -> NoteRead:
    return NoteRead(id=note.id, title=note.title, content=note.content, created_at=note.created_at)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", llm_provider=settings.llm_provider)


@app.post("/notes", response_model=NoteRead, status_code=201, tags=["notes"])
def api_create_note(payload: NoteCreate, session: Session = Depends(get_session)) -> NoteRead:
    settings = get_settings()
    note = create_note(session, settings, payload.title, payload.content)
    return _to_read(note)


@app.get("/notes", response_model=list[NoteRead], tags=["notes"])
def api_list_notes(session: Session = Depends(get_session)) -> list[NoteRead]:
    return [_to_read(n) for n in list_notes(session)]


@app.get("/notes/{note_id}", response_model=NoteRead, tags=["notes"])
def api_get_note(note_id: str, session: Session = Depends(get_session)) -> NoteRead:
    try:
        note = get_note(session, note_id)
    except NoteNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_read(note)


@app.delete("/notes/{note_id}", status_code=204, tags=["notes"])
def api_delete_note(note_id: str, session: Session = Depends(get_session)) -> None:
    try:
        delete_note(session, note_id)
    except NoteNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/notes/{note_id}/summarize", response_model=SummarizeResponse, tags=["ai"])
def api_summarize_note(note_id: str, session: Session = Depends(get_session)) -> SummarizeResponse:
    settings = get_settings()
    try:
        summary = summarize_note(session, settings, note_id)
    except NoteNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SummarizeResponse(summary=summary)


@app.post("/search", response_model=list[SearchResultItem], tags=["ai"])
def api_search(
    payload: SearchRequest, session: Session = Depends(get_session)
) -> list[SearchResultItem]:
    settings = get_settings()
    results = search_notes(session, settings, payload.query)
    return [SearchResultItem(note=_to_read(n), score=score) for n, score in results]


@app.post("/chat", response_model=ChatResponse, tags=["ai"])
def api_chat(payload: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    settings = get_settings()
    answer, source_ids = chat_with_notes(session, settings, payload.message)
    return ChatResponse(answer=answer, source_note_ids=source_ids)
