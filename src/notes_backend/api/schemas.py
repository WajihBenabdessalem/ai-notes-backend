"""Schémas Pydantic des requêtes/réponses de l'API."""

from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class NoteRead(BaseModel):
    id: str
    title: str
    content: str
    created_at: datetime


class SummarizeResponse(BaseModel):
    summary: str


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)


class SearchResultItem(BaseModel):
    note: NoteRead
    score: float


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    answer: str
    source_note_ids: list[str]


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
