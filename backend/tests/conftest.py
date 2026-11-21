import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers tables)
from app.config import get_settings
from app.db import Base, get_db, get_session_factory
from app.main import app


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    """Every test gets its own empty, encrypted storage folder."""
    s = get_settings()
    monkeypatch.setattr(s, "storage_dir", tmp_path / "storage")
    monkeypatch.setattr(s, "file_encryption_key", None)
    return tmp_path / "storage"


@pytest.fixture(autouse=True)
def offline_by_default(monkeypatch):
    """Tests never call a real AI API and don't load the embedding model unless they opt in,
    even when keys are set in backend/.env."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(get_settings(), "anthropic_api_key", None)
    monkeypatch.setattr(get_settings(), "groq_api_key", None)
    monkeypatch.setattr(get_settings(), "ai_provider", "auto")
    monkeypatch.setattr(get_settings(), "embeddings_enabled", False)


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    engine.dispose()


@pytest.fixture
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session, session_factory):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_session_factory] = lambda: session_factory
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    r = client.post(
        "/api/auth/signup",
        json={"full_name": "Test User", "email": "test.user@example.com", "password": "test-pass-123"},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
