from sqlalchemy import select

from app.config import get_settings
from app.models import Policy
from app.routers.documents import _clean_filename
from app.seed import seed

from .doc_factory import CLAUSE_LINES, password_pdf, photo, scanned_pdf, text_pdf


def upload(client, headers, data: bytes, name="policy.pdf", kind="policy_wording", policy_id=None):
    form = {"kind": kind}
    if policy_id is not None:
        form["policy_id"] = str(policy_id)
    return client.post("/api/documents", headers=headers, data=form, files={"file": (name, data, "application/octet-stream")})


def demo_headers(client):
    s = get_settings()
    r = client.post("/api/auth/login", json={"email": s.demo_email, "password": s.demo_password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_upload_digital_pdf_and_read_pages(client, auth_headers, isolated_storage):
    r = upload(client, auth_headers, text_pdf([CLAUSE_LINES, ["5.1 Room rent limit"]]))
    assert r.status_code == 201
    doc = r.json()
    assert doc["content_type"] == "application/pdf" and doc["filename"] == "policy.pdf"

    # TestClient runs background tasks before returning, so it's already processed.
    doc = client.get(f"/api/documents/{doc['id']}", headers=auth_headers).json()
    assert doc["status"] == "ready" and doc["page_count"] == 2 and doc["ocr_pages"] == 0

    pages = client.get(f"/api/documents/{doc['id']}/pages", headers=auth_headers).json()
    assert [p["page_number"] for p in pages] == [1, 2]
    assert "24 months" in pages[0]["text"] and pages[0]["method"] == "text"

    # The stored file is encrypted
    stored = [f for f in isolated_storage.iterdir() if f.suffix == ".bin"]
    assert len(stored) == 1 and b"Waiting period" not in stored[0].read_bytes()


def test_upload_scan_and_photo_use_ocr(client, auth_headers):
    scan = upload(client, auth_headers, scanned_pdf([CLAUSE_LINES]), name="scan.pdf").json()
    pic = upload(client, auth_headers, photo(), name="IMG_2041.jpg", kind="rejection_letter").json()
    scan = client.get(f"/api/documents/{scan['id']}", headers=auth_headers).json()
    pic = client.get(f"/api/documents/{pic['id']}", headers=auth_headers).json()
    assert scan["status"] == "ready" and scan["ocr_pages"] == 1
    assert pic["status"] == "ready" and pic["content_type"] == "image/jpeg" and pic["kind"] == "rejection_letter"


def test_failed_reading_is_reported(client, auth_headers):
    doc = upload(client, auth_headers, password_pdf()).json()
    doc = client.get(f"/api/documents/{doc['id']}", headers=auth_headers).json()
    assert doc["status"] == "failed" and doc["error"] == "password_protected"


def test_rejects_unsupported_empty_and_large_files(client, auth_headers, monkeypatch):
    assert upload(client, auth_headers, b"PK\x03\x04 docx", name="policy.docx").json()["detail"] == "unsupported_type"
    assert upload(client, auth_headers, b"").json()["detail"] == "empty_file"
    monkeypatch.setattr(get_settings(), "max_upload_mb", 0)
    r = upload(client, auth_headers, text_pdf([CLAUSE_LINES]))
    assert r.status_code == 413 and r.json()["detail"] == "file_too_large"


def test_rejects_unknown_kind(client, auth_headers):
    assert upload(client, auth_headers, text_pdf([CLAUSE_LINES]), kind="selfie").status_code == 422


def test_filename_is_cleaned(client, auth_headers):
    doc = upload(client, auth_headers, text_pdf([CLAUSE_LINES]), name="C:\\Users\\x\\..\\my policy.pdf").json()
    assert doc["filename"] == "my policy.pdf"
    # control characters (the test client percent-encodes them, so check the function directly)
    assert _clean_filename("../../etc/pass\x07wd\n") == "passwd"
    assert _clean_filename(None) == "document"


def test_change_document_type(client, db_session, auth_headers):
    doc = upload(client, auth_headers, photo(), name="letter.jpg").json()
    assert doc["kind"] == "policy_wording"
    r = client.patch(f"/api/documents/{doc['id']}", headers=auth_headers, json={"kind": "rejection_letter"})
    assert r.status_code == 200 and r.json()["kind"] == "rejection_letter"
    assert client.get(f"/api/documents/{doc['id']}", headers=auth_headers).json()["kind"] == "rejection_letter"
    assert client.patch(f"/api/documents/{doc['id']}", headers=auth_headers, json={"kind": "selfie"}).status_code == 422

    seed(db_session)
    assert client.patch(f"/api/documents/{doc['id']}", headers=demo_headers(client), json={"kind": "other"}).status_code == 404


def test_download_returns_original_file(client, auth_headers):
    pdf = text_pdf([CLAUSE_LINES])
    doc = upload(client, auth_headers, pdf).json()
    r = client.get(f"/api/documents/{doc['id']}/file", headers=auth_headers)
    assert r.content == pdf and r.headers["content-type"] == "application/pdf"
    assert "no-store" in r.headers["cache-control"]


def test_delete_removes_file_and_rows(client, auth_headers, isolated_storage):
    doc = upload(client, auth_headers, text_pdf([CLAUSE_LINES])).json()
    assert client.delete(f"/api/documents/{doc['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/documents/{doc['id']}", headers=auth_headers).status_code == 404
    assert not [f for f in isolated_storage.iterdir() if f.suffix == ".bin"]


def test_documents_are_private(client, db_session, auth_headers):
    seed(db_session)
    demo = demo_headers(client)
    doc = upload(client, demo, text_pdf([CLAUSE_LINES])).json()
    for path in ("", "/pages", "/file"):
        assert client.get(f"/api/documents/{doc['id']}{path}", headers=auth_headers).status_code == 404
    assert client.delete(f"/api/documents/{doc['id']}", headers=auth_headers).status_code == 404
    assert client.get("/api/documents", headers=auth_headers).json() == []


def test_attach_to_policy_and_delete_policy_removes_files(client, db_session, isolated_storage):
    seed(db_session)
    demo = demo_headers(client)
    policy_id = client.get("/api/policies", headers=demo).json()[0]["id"]

    doc = upload(client, demo, text_pdf([CLAUSE_LINES]), policy_id=policy_id).json()
    assert doc["policy_id"] == policy_id
    assert len(client.get(f"/api/documents?policy_id={policy_id}", headers=demo).json()) == 1

    assert client.delete(f"/api/policies/{policy_id}", headers=demo).status_code == 204
    assert client.get(f"/api/documents/{doc['id']}", headers=demo).status_code == 404
    assert not [f for f in isolated_storage.iterdir() if f.suffix == ".bin"]


def test_cannot_attach_to_someone_elses_policy(client, db_session, auth_headers):
    seed(db_session)
    other_policy = db_session.scalars(select(Policy)).first()
    r = upload(client, auth_headers, text_pdf([CLAUSE_LINES]), policy_id=other_policy.id)
    assert r.status_code == 404
