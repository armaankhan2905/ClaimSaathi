from datetime import date

import pymupdf

from app import complaints as cp
from app.understanding.claims import check_claim

from .test_claims import CLAUSE_5, CLAUSE_42, LETTER, SAMPLES, needs_samples, terms
from .test_documents import upload


def demo_findings():
    facts, findings, _ = check_claim(LETTER, {}, terms(), [CLAUSE_42, CLAUSE_5], True, "en", None)
    return facts.model_dump() if hasattr(facts, "model_dump") else facts, findings


def demo_fields(**over):
    facts, findings = demo_findings()
    f = {
        "name": "Rohit Sharma", "phone": "98XXX XX214", "email": "rohit@example.com", "address": "", "insurer": "Navjeevan General Insurance",
        "policy_number": "NGI/HL/2026/448812", "claim_number": "CLM-26-08817", "amount": 180000, "patient": "Rohit Sharma",
        "hospital": "Sample Multispeciality Hospital, Bengaluru", "treatment": "left total knee replacement", "admission_date": "2026-09-14",
        "letter_date": "2026-10-03", "grievance_type": "claim_rejected", "ask": cp.default_ask(facts, findings),
        "grounds": cp.grounds_from_findings(findings), "attachments": [], "include_report": True, "situation": "not_yet",
        "earlier_complaint_date": None, "earlier_reference": "", "insurer_reply_date": None,
    }
    f.update(over)
    return f


def test_grounds_and_ask_come_from_the_check():
    facts, findings = demo_findings()
    grounds = cp.grounds_from_findings(findings)
    assert grounds[0]["ref"] == "4.2" and "First Policy Date" in grounds[0]["text"] and "12 Mar 2024" in grounds[0]["text"]
    assert any("renewed without a break since 12 Mar 2022" in g["text"] for g in grounds)
    assert any("latest renewal date" in g["text"] for g in grounds)
    ask = cp.default_ask(facts, findings)
    assert "Rs. 1,80,000" in ask and "Clause 4.2 ended on 12 Mar 2024" in ask
    assert cp.grounds_from_findings(None) == []


def test_letters_for_each_stage():
    f = demo_fields()
    today = date(2026, 11, 21)
    ins = cp.build_letter("insurer", f, [], [], True, today)
    text = cp.letter_text(ins)
    assert ins["to"] == "The Grievance Redressal Officer, Navjeevan General Insurance"
    assert "Request to review the rejection of claim CLM-26-08817" in text and "rejected by your letter dated 3 Oct 2026" in text
    assert "[Clause 4.2]" in text and "within 14 days" in text and "ClaimSaathi evidence report (PDF)" in text
    assert "Mobile: 98XXX XX214" in text and text.count("Yours faithfully") == 1

    history = [{"kind": "sent", "stage": "insurer", "date": "2026-10-10", "reference": "GRV-55120"},
               {"kind": "reply", "stage": "insurer", "date": "2026-10-20", "outcome": "unsatisfied"}]
    bb = cp.letter_text(cp.build_letter("bima_bharosa", f, history, [], False, today))
    assert "Complaint against Navjeevan General Insurance" in bb
    assert "on 10 Oct 2026 (reference GRV-55120)" in bb and "replied on 20 Oct 2026" in bb
    assert "evidence report" not in bb  # no report without a finished check

    om = cp.letter_text(cp.build_letter("ombudsman", f, history + [{"kind": "sent", "stage": "bima_bharosa", "date": "2026-10-22", "reference": "BB-1"}], [], True, today))
    assert "Rule 14 of the Insurance Ombudsman Rules, 2017" in om and "not pending before" in om
    assert "Bima Bharosa portal on 22 Oct 2026 (reference BB-1)" in om and "Amount in dispute: Rs. 1,80,000" in om


def test_earlier_steps_taken_outside_claimsaathi_go_in_the_letter():
    f = demo_fields(situation="no_reply", earlier_complaint_date="2026-10-05", earlier_reference="NGI-778")
    text = cp.letter_text(cp.build_letter("bima_bharosa", f, [], [], False, date(2026, 11, 21)))
    assert "on 5 Oct 2026 (reference NGI-778)" in text and "not received a reply" in text
    assert cp.recommended_stage(f) == "bima_bharosa"
    assert cp.recommended_stage(demo_fields(situation="bb_unresolved")) == "ombudsman"


def test_deadlines_and_when_you_can_escalate():
    f = demo_fields()
    sent = [{"kind": "sent", "stage": "insurer", "date": "2026-11-01", "reference": ""}]
    t = cp.tracker("insurer", "sent", f, sent, today=date(2026, 11, 5))
    assert (t["reply_due"], t["days_left"], t["can_escalate"]) == ("2026-11-15", 10, [])
    assert (t["ombudsman_from"], t["ombudsman_by"]) == ("2026-12-01", "2027-12-01")
    assert cp.tracker("insurer", "sent", f, sent, today=date(2026, 11, 15))["can_escalate"] == ["bima_bharosa"]
    assert cp.tracker("insurer", "sent", f, sent, today=date(2026, 12, 1))["can_escalate"] == ["bima_bharosa", "ombudsman"]
    assert cp.tracker("insurer", "sent", f, sent, today=date(2028, 1, 1))["can_escalate"] == ["bima_bharosa"]  # too late for the Ombudsman

    replied = sent + [{"kind": "reply", "stage": "insurer", "date": "2026-11-04", "outcome": "unsatisfied"}]
    t = cp.tracker("insurer", "sent", f, replied, today=date(2026, 11, 5))
    assert t["can_escalate"] == ["bima_bharosa", "ombudsman"] and t["days_left"] is None and t["ombudsman_by"] == "2027-11-04"
    assert cp.tracker("insurer", "draft", f, [], today=date(2026, 11, 5))["can_escalate"] == []

    ics = cp.reminder_ics(7, "insurer", f, cp.tracker("insurer", "sent", f, sent, today=date(2026, 11, 5)))
    assert "DTSTART;VALUE=DATE:20261115" in ics and "TRIGGER:-P1D" in ics and "CLM-26-08817" in ics


def test_clean_fields_keeps_known_shapes():
    out = cp.clean_fields({"name": "A"}, {"name": "B", "evil": "x", "amount": "abc", "situation": "nope",
                                          "grounds": [{"text": "t", "ref": "4.2"}, "bad"], "attachments": ["3", "x"], "insurer_reply_date": "2026-10-20T00:00"})
    assert out == {"name": "B", "amount": None, "grounds": [{"text": "t", "ref": "4.2"}], "attachments": [3], "insurer_reply_date": "2026-10-20"}


# ---------- through the API, from a real Rejection Check ----------

def _checked_claim(client, auth_headers):
    for name, kind in [("suraksha-health-plus-policy-wording.pdf", "policy_wording"), ("suraksha-health-plus-policy-schedule.pdf", "policy_schedule")]:
        upload(client, auth_headers, (SAMPLES / name).read_bytes(), name=name, kind=kind)
    claim = client.post("/api/claims", json={}, headers=auth_headers).json()
    client.post("/api/documents", headers=auth_headers, data={"kind": "rejection_letter", "claim_id": str(claim["id"])},
                files={"file": ("letter.jpg", (SAMPLES / "rejection-letter-CLM-26-08817-photo.jpg").read_bytes(), "image/jpeg")})
    client.post(f"/api/claims/{claim['id']}/check", json={}, headers=auth_headers)
    return client.get(f"/api/claims/{claim['id']}", headers=auth_headers).json()


@needs_samples
def test_complaint_end_to_end(client, auth_headers, isolated_storage):
    claim = _checked_claim(client, auth_headers)
    r = client.post("/api/complaints", json={"claim_id": claim["id"]}, headers=auth_headers)
    assert r.status_code == 201
    c = r.json()
    f = c["fields"]
    assert (c["stage"], c["status"], c["recommended_stage"]) == ("insurer", "draft", "insurer")
    assert f["claim_number"] == "CLM-26-08817" and f["amount"] == 180000 and f["insurer"] and f["policy_number"]
    assert f["grounds"][0]["ref"] == "4.2" and c["has_report"] is True
    names = {o["filename"]: o["id"] for o in c["attachment_options"]}
    assert "letter.jpg" in names and "suraksha-health-plus-policy-schedule.pdf" in names
    assert names["suraksha-health-plus-policy-wording.pdf"] not in f["attachments"]  # the long wording isn't attached by default

    c = client.patch(f"/api/complaints/{c['id']}", json={"fields": {"phone": "98XXX XX214", "attachments": [names["letter.jpg"], 99999]}}, headers=auth_headers).json()
    assert c["fields"]["attachments"] == [names["letter.jpg"]]  # someone else's document id is dropped
    assert "Mobile: 98XXX XX214" in c["letter_text"] and "- letter.jpg" in c["letter_text"]

    letter = client.get(f"/api/complaints/{c['id']}/letter", headers=auth_headers)
    assert letter.status_code == 200 and letter.content.startswith(b"%PDF")
    letter_pages = pymupdf.open(stream=letter.content, filetype="pdf").page_count
    pkg = client.get(f"/api/complaints/{c['id']}/package", headers=auth_headers)
    doc = pymupdf.open(stream=pkg.content, filetype="pdf")
    assert doc.page_count >= letter_pages + 2  # letter + evidence report + the letter photo
    text = " ".join("".join(p.get_text() for p in doc).split())
    assert "Grievance Redressal" in text and "Enclosure 1: ClaimSaathi evidence report" in text and "Enclosure 2: letter.jpg" in text

    assert client.get(f"/api/complaints/{c['id']}/reminder", headers=auth_headers).status_code == 409  # not sent yet
    c = client.post(f"/api/complaints/{c['id']}/sent", json={"reference": "GRV-55120"}, headers=auth_headers).json()
    assert c["status"] == "sent" and c["tracker"]["reference"] == "GRV-55120" and c["tracker"]["days_left"] == 14
    assert client.patch(f"/api/complaints/{c['id']}", json={"stage": "ombudsman"}, headers=auth_headers).status_code == 409
    ics = client.get(f"/api/complaints/{c['id']}/reminder", headers=auth_headers)
    assert ics.status_code == 200 and ics.headers["content-type"].startswith("text/calendar")

    assert client.post(f"/api/complaints/{c['id']}/escalate", json={"to": "bima_bharosa"}, headers=auth_headers).json()["detail"] == "cannot_escalate_yet"
    c = client.post(f"/api/complaints/{c['id']}/reply", json={"outcome": "unsatisfied"}, headers=auth_headers).json()
    assert c["tracker"]["can_escalate"] == ["bima_bharosa", "ombudsman"]
    c = client.post(f"/api/complaints/{c['id']}/escalate", json={"to": "bima_bharosa"}, headers=auth_headers).json()
    assert (c["stage"], c["status"]) == ("bima_bharosa", "draft")
    assert "(reference GRV-55120)" in c["letter_text"] and "does not resolve my complaint" in c["letter_text"]
    assert [e["kind"] for e in c["history"]] == ["created", "sent", "reply", "escalated"]

    # deleting the check keeps the complaint
    assert client.delete(f"/api/claims/{claim['id']}", headers=auth_headers).status_code == 204
    c = client.get(f"/api/complaints/{c['id']}", headers=auth_headers).json()
    assert c["claim_id"] is None and c["has_report"] is False and c["fields"]["claim_number"] == "CLM-26-08817"


def test_complaint_without_a_check_and_resolving(client, auth_headers):
    c = client.post("/api/complaints", json={"situation": "no_reply"}, headers=auth_headers).json()
    assert c["stage"] == "bima_bharosa" and c["fields"]["grounds"] == [] and c["attachment_options"] == []
    c = client.post(f"/api/complaints/{c['id']}/sent", json={"sent_on": "2026-01-01"}, headers=auth_headers).json()
    c = client.post(f"/api/complaints/{c['id']}/reply", json={"outcome": "resolved"}, headers=auth_headers).json()
    assert c["status"] == "resolved" and c["tracker"]["can_escalate"] == []
    assert client.post(f"/api/complaints/{c['id']}/sent", json={"sent_on": "2999-01-01"}, headers=auth_headers).status_code == 409


def test_complaints_are_private(client, db_session, auth_headers):
    from app.seed import seed

    from .test_documents import demo_headers

    c = client.post("/api/complaints", json={}, headers=auth_headers).json()
    seed(db_session)
    demo = demo_headers(client)
    for method, path in [("get", ""), ("patch", ""), ("post", "/sent"), ("get", "/letter"), ("get", "/package"), ("delete", "")]:
        kw = {"json": {}} if method in ("post", "patch") else {}
        assert getattr(client, method)(f"/api/complaints/{c['id']}{path}", headers=demo, **kw).status_code == 404, (method, path)
    assert client.get("/api/complaints", headers=demo).json() == []
    other_claim = client.post("/api/claims", json={}, headers=demo).json()
    assert client.post("/api/complaints", json={"claim_id": other_claim["id"]}, headers=auth_headers).status_code == 404
