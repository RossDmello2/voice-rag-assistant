import asyncio
import shutil
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.routes import collections as collections_routes
from app.api.routes import ingest as ingest_routes
from app.core.config import Settings
from app.core.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    runtime_dir = Path(__file__).resolve().parents[2] / ".test_runtime"
    runtime_dir.mkdir(exist_ok=True)
    db_path = runtime_dir / f"test_voice_agent_{uuid.uuid4().hex}.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)
    session_local = async_sessionmaker(engine, expire_on_commit=False)

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup_db())

    async def override_get_db():
        async with session_local() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()
        asyncio.run(engine.dispose())
        shutil.rmtree(runtime_dir, ignore_errors=True)


def register_and_get_token(client: TestClient) -> str:
    response = client.post(
        "/auth/register",
        json={"email": "tester@example.com", "password": "strong-password"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token_type"] == "bearer"
    return body["access_token"]


def test_auth_routes_are_mounted_and_login_works(client):
    token = register_and_get_token(client)
    assert token

    login = client.post(
        "/auth/login",
        data={"username": "tester@example.com", "password": "strong-password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200, login.text
    assert login.json()["access_token"]


def test_mutating_collection_routes_require_auth(client):
    create_response = client.post("/collections", json={"name": "agent_knowledge"})
    delete_response = client.delete("/collections/agent_knowledge")
    document_delete_response = client.delete("/collections/agent_knowledge/documents/file.txt")

    assert create_response.status_code == 401
    assert delete_response.status_code == 401
    assert document_delete_response.status_code == 401
    assert create_response.headers["www-authenticate"] == "Bearer"


def test_authorized_collection_create_uses_token(client, monkeypatch):
    token = register_and_get_token(client)

    async def fake_create_collection(name: str, vector_size: int):
        return {"status": "ok", "result": True, "name": name, "vector_size": vector_size}

    monkeypatch.setattr(collections_routes, "create_collection", fake_create_collection)

    response = client.post(
        "/collections",
        json={"name": "agent_knowledge"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "created"


def test_ingest_requires_auth(client):
    response = client.post(
        "/ingest",
        files={"file": ("sample.txt", b"hello world " * 8, "text/plain")},
        data={"collection": "agent_knowledge"},
    )
    assert response.status_code == 401


def test_ingest_endpoint_uses_sanitized_filename(client, monkeypatch):
    token = register_and_get_token(client)
    captured = {}

    async def fake_ingest_document(file_bytes, filename, collection, embed_model=None):
        captured["filename"] = filename
        captured["collection"] = collection
        return 3

    monkeypatch.setattr(ingest_routes, "ingest_document", fake_ingest_document)

    response = client.post(
        "/ingest",
        files={"file": ("../bad name!!.txt", b"hello world " * 8, "text/plain")},
        data={"collection": "agent_knowledge"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    assert captured["filename"] == "badname.txt"
    assert response.json()["filename"] == "badname.txt"


def test_ingest_document_fails_when_qdrant_upsert_is_not_acknowledged(monkeypatch):
    async def fake_list_collections():
        return ["agent_knowledge"]

    async def fake_generate_embedding(text, model=None):
        return [0.0] * 768

    async def fake_upsert_points(collection, points):
        return {"result": {}}

    monkeypatch.setattr(ingest_routes, "list_collections", fake_list_collections)
    monkeypatch.setattr(ingest_routes, "generate_embedding", fake_generate_embedding)
    monkeypatch.setattr(ingest_routes, "upsert_points", fake_upsert_points)

    with pytest.raises(Exception) as exc_info:
        asyncio.run(
            ingest_routes.ingest_document(
                b"This is a readable text document. " * 8,
                "safe.txt",
                "agent_knowledge",
            )
        )

    assert getattr(exc_info.value, "status_code", None) == 502
    assert "Vector store write failed" in exc_info.value.detail


def test_production_env_rejects_fallback_secret():
    with pytest.raises(ValidationError):
        Settings(
            APP_ENV="production",
            SECRET_KEY="fallback_secret_key_change_me_in_production",
        )
