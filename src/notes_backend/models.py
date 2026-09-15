"""Modèle de persistance des notes (table SQLite), embedding stocké en JSON."""

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str
    content: str
    embedding_json: str = Field(default="[]")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def get_embedding(self) -> list[float]:
        return json.loads(self.embedding_json)

    def set_embedding(self, embedding: list[float]) -> None:
        self.embedding_json = json.dumps(embedding)
