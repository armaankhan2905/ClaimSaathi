"""Production readiness: settings checks, security headers, sign-in limit, serving the built site, demo data."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import DEV_JWT_SECRET, Settings, get_settings
from app.main import serve_site

from .test_claims import SAMPLES, needs_samples


def test_production_needs_real_secrets():
    s = Settings(_env_file=None, app_env="production", jwt_secret=DEV_JWT_SECRET, file_encryption_key=None)
    assert s.is_production and len(s.production_problems()) == 2
    ok = Settings(_env_file=None, app_env="production", jwt_secret="x" * 48, file_encryption_key="k")
    assert ok.production_problems() == []
    assert Settings(_env_file=None, app_env="production", jwt_secret="x" * 48, file_encryption_key="k", seed_demo=True, demo_password="").production_problems()
    assert not Settings(_env_file=None).is_production


def test_security_headers(client):
    r = client.get("/api/health")
    assert r.json() == {"status": "ok"}
    assert r.headers["x-content-type-options"] == "nosniff" and r.headers["x-frame-options"] == "DENY"
    assert "strict-transport-security" not in r.headers  # only behind HTTPS in production


def test_sign_in_is_limited_after_repeated_failures(client, monkeypatch):
    from app.routers import auth

    monkeypatch.setattr(get_settings(), "login_attempts", 3)
    monkeypatch.setattr(auth, "_failures", type(auth._failures)(auth._failures.default_factory))
    client.post("/api/auth/signup", json={"full_name": "A", "email": "a@example.com", "password": "right-pass-1"})
    for _ in range(3):
        assert client.post("/api/auth/login", json={"email": "a@example.com", "password": "wrong-pass"}).status_code == 401
    r = client.post("/api/auth/login", json={"email": "a@example.com", "password": "right-pass-1"})
    assert r.status_code == 429 and r.json()["detail"] == "too_many_attempts"
    # someone else's email isn't affected
    assert client.post("/api/auth/login", json={"email": "b@example.com", "password": "x"}).status_code == 401


def test_serves_the_built_site_with_app_routes(tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><div id=root></div>")
    (dist / "assets" / "app-123.js").write_text("console.log(1)")
    (tmp_path / "secret.txt").write_text("no")
    site = FastAPI()

    @site.get("/api/health")
    def health():
        return {"status": "ok"}

    serve_site(site, dist)
    c = TestClient(site)
    assert c.get("/api/health").json() == {"status": "ok"}
    assert "id=root" in c.get("/").text and "id=root" in c.get("/rejection?claim=1").text  # app routes get the page
    a = c.get("/assets/app-123.js")
    assert a.text == "console.log(1)" and "immutable" in a.headers["cache-control"]
    assert c.get("/api/nope").status_code == 404  # unknown API paths stay errors, not the page
    assert "no" != c.get("/../secret.txt").text and "id=root" in c.get("/%2e%2e/secret.txt").text


@needs_samples
def test_demo_documents_load_once(session_factory, isolated_storage):
    from app.models import Document, Policy
    from app.seed import load_sample_documents, seed

    with session_factory() as db:
        user = seed(db)
    assert load_sample_documents(user.id, session_factory, SAMPLES) == 6
    assert load_sample_documents(user.id, session_factory, SAMPLES) == 0  # safe to run again
    with session_factory() as db:
        docs = db.query(Document).filter_by(owner_id=user.id).all()
        assert len(docs) == 6 and all(d.status == "ready" for d in docs)
        suraksha = db.query(Policy).filter_by(owner_id=user.id, policy_number="NGI/HL/2026/448812").one()
        assert {d.kind for d in docs if d.policy_id == suraksha.id} == {"policy_wording", "policy_schedule"}
        assert db.query(Policy).filter(Policy.owner_id == user.id, Policy.name.like("%Arogya%")).count() == 1


@pytest.mark.parametrize("path", ["/docs", "/openapi.json"])
def test_api_docs_are_available_in_development(client, path):
    assert client.get(path).status_code == 200
