"""Connexion à la base de données (SQLite via SQLModel)."""

from pathlib import Path

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from notes_backend.config import get_settings


def _make_engine():
    settings = get_settings()
    url = settings.database_url

    if url == "sqlite://":
        # Base en mémoire (tests) : une seule connexion partagée via StaticPool.
        return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)

    if url.startswith("sqlite:///"):
        db_path = url.replace("sqlite:///", "", 1)
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return create_engine(url, connect_args={"check_same_thread": False})

    return create_engine(url)


engine = _make_engine()


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
