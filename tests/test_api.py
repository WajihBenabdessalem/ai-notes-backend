import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from notes_backend.api.main import app
from notes_backend.db import get_session


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_list_notes(client):
    create_response = client.post("/notes", json={"title": "Titre", "content": "Contenu"})
    assert create_response.status_code == 201
    note_id = create_response.json()["id"]

    list_response = client.get("/notes")
    assert list_response.status_code == 200
    assert any(n["id"] == note_id for n in list_response.json())


def test_get_missing_note_returns_404(client):
    response = client.get("/notes/id-inexistant")
    assert response.status_code == 404


def test_create_note_rejects_empty_title(client):
    response = client.post("/notes", json={"title": "", "content": "Contenu"})
    assert response.status_code == 422


def test_summarize_endpoint_returns_summary(client):
    note_id = client.post("/notes", json={"title": "T", "content": "C"}).json()["id"]

    response = client.post(f"/notes/{note_id}/summarize")

    assert response.status_code == 200
    assert "summary" in response.json()


def test_summarize_missing_note_returns_404(client):
    response = client.post("/notes/id-inexistant/summarize")
    assert response.status_code == 404


def test_search_endpoint_returns_matching_note(client):
    created = client.post("/notes", json={"title": "Congés", "content": "25 jours de congés"})
    note_id = created.json()["id"]

    response = client.post("/search", json={"query": "Congés\n25 jours de congés"})

    assert response.status_code == 200
    body = response.json()
    assert body
    assert body[0]["note"]["id"] == note_id


def test_chat_endpoint_returns_answer(client):
    client.post("/notes", json={"title": "Congés", "content": "25 jours de congés"})

    response = client.post("/chat", json={"message": "Congés\n25 jours de congés"})

    assert response.status_code == 200
    assert "source_note_ids" in response.json()


def test_delete_note(client):
    note_id = client.post("/notes", json={"title": "X", "content": "Y"}).json()["id"]

    delete_response = client.delete(f"/notes/{note_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/notes/{note_id}")
    assert get_response.status_code == 404
