"""Configuration partagée des tests.

On force `OPENAI_API_KEY` à vide pour garantir un comportement déterministe et hors ligne :
les modules `embeddings.py` / `llm.py` basculent alors sur leur repli local, ce qui permet
de tester tout le pipeline (notes -> embedding -> recherche -> chat) sans réseau ni clé API.
"""

import os

os.environ["OPENAI_API_KEY"] = ""
os.environ["LLM_PROVIDER"] = "openai"
os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from notes_backend.config import Settings  # noqa: E402


@pytest.fixture
def settings() -> Settings:
    return Settings(openai_api_key=None, database_url="sqlite://")


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
