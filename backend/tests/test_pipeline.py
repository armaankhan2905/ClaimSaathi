"""Uploading policy documents produces an understood policy card (basic mode, no API calls)."""

from app.seed import seed
from app.understanding.kinds import suggest_kind
from app.understanding.labels import ClauseLabel, ClauseLabels
from app.understanding.terms import PolicyTerms

from .doc_factory import text_pdf
from .fake_ai import FakeAI
from .test_documents import demo_headers, upload

WORDING = [
    ["Suraksha Health Plus - Policy Wording", "Navjeevan General Insurance Company Limited", "1. Preamble",
     "This Policy is a contract between you and the Company for hospitalisation.", "2. Definitions", "2.1 Grace Period",
     "The period of 30 days after expiry during which the policy may be renewed."],
    ["4. Waiting periods", "4.1 Initial waiting period", "Nothing is payable within the first 30 days from the First Policy Date.",
     "4.2 Specified illnesses and procedures", "Joint replacement surgery, including knee replacement, is payable only",
     "after 24 months of Continuous Coverage from the First Policy Date.", "5. Exclusions", "The Company will not pay for cosmetic surgery."],
]
SCHEDULE = [["Policy Schedule", "Suraksha Health Plus - Navjeevan General Insurance Company Limited", "Policy number NGI/HL/2026/448812",
             "Policyholder Rohit Sharma", "Policy period 12 Mar 2026 to 11 Mar 2027", "First Policy Date 12 Mar 2022",
             "Sum Insured Rs. 5,00,000", "Co-payment 10% outside network hospitals",
             "NGI/HL/2022/118204 12 Mar 2022 - 11 Mar 2023", "NGI/HL/2023/207731 12 Mar 2023 - 11 Mar 2024",
             "NGI/HL/2024/310962 12 Mar 2024 - 11 Mar 2025", "NGI/HL/2025/389457 12 Mar 2025 - 11 Mar 2026"]]
# (Leaving out a year makes the rules engine report a break in cover, as it should.)


def _policies(client, headers):
    return client.get("/api/policies", headers=headers).json()


def test_upload_wording_creates_understood_policy(client, auth_headers):
    upload(client, auth_headers, text_pdf(WORDING), name="suraksha-wording.pdf")
    [p] = _policies(client, auth_headers)
    assert p["name"] == "Suraksha Health Plus" and p["insurer"] == "Navjeevan General Insurance Company Limited"
    assert p["category"] == "health" and p["status"] == "active" and p["auto_created"] is False
    assert (p["analysis_status"], p["analysis_mode"], p["clause_count"]) == ("ready", "basic", 5)

    clauses = client.get(f"/api/policies/{p['id']}/clauses", headers=auth_headers).json()
    assert [c["ref"] for c in clauses] == ["1", "2.1", "4.1", "4.2", "5"]
    assert {c["ref"]: c["category"] for c in clauses}["4.2"] == "waiting_period"
    assert clauses[3]["page_start"] == 2 and clauses[3]["plain"] is None  # no explanations without AI


def test_wording_and_schedule_merge_into_one_policy(client, auth_headers):
    upload(client, auth_headers, text_pdf(WORDING), name="suraksha-health-plus-policy-wording.pdf")
    upload(client, auth_headers, text_pdf(SCHEDULE), name="schedule.pdf", kind="policy_schedule")
    [p] = _policies(client, auth_headers)
    assert p["policy_number"] == "NGI/HL/2026/448812" and p["sum_insured"] == 500000
    assert (p["cover_since"], p["renews_on"]) == ("2022-03-12", "2027-03-11")

    detail = client.get(f"/api/policies/{p['id']}", headers=auth_headers).json()
    assert detail["terms"]["policyholder"] == "Rohit Sharma"
    wp = {w["clause_ref"]: w for w in detail["timeline"]["waiting_periods"]}
    assert wp["4.2"]["ends"] == "2024-03-12" and wp["4.2"]["completed"] is True
    docs = client.get("/api/documents", headers=auth_headers).json()
    assert {d["policy_id"] for d in docs} == {p["id"]}


def test_upload_merges_into_existing_seeded_policy(client, db_session):
    seed(db_session)
    demo = demo_headers(client)
    upload(client, demo, text_pdf(SCHEDULE), name="schedule.pdf", kind="policy_schedule")
    policies = _policies(client, demo)
    assert len(policies) == 2  # merged into the seeded Suraksha card by policy number, not a third card
    suraksha = next(p for p in policies if p["name"] == "Suraksha Health Plus")
    assert suraksha["analysis_status"] == "ready" and suraksha["renews_on"] == "2027-03-11"


def test_rejection_letter_labelled_as_wording_does_not_create_policy(client, auth_headers):
    letter = text_pdf([["Navjeevan General Insurance - Claims", "Subject: Repudiation of claim CLM-26-08817",
                        "We regret to inform you that the claim is not payable."]])
    doc = upload(client, auth_headers, letter, name="letter.pdf").json()
    doc = client.get(f"/api/documents/{doc['id']}", headers=auth_headers).json()
    assert doc["suggested_kind"] == "rejection_letter" and doc["policy_id"] is None
    assert _policies(client, auth_headers) == []


def test_deleting_the_only_document_of_a_new_policy(client, auth_headers):
    doc = upload(client, auth_headers, text_pdf([["Policy Schedule", "Policy number X/1/2", "Sum Insured Rs. 1,00,000"]]),
                 name="mystery.pdf", kind="policy_schedule").json()
    [p] = _policies(client, auth_headers)
    assert p["auto_created"] is True and p["name"] == "Mystery"  # no plan name found: placeholder from the file name
    client.delete(f"/api/documents/{doc['id']}", headers=auth_headers)
    assert _policies(client, auth_headers) == []


def test_search_endpoint(client, auth_headers):
    upload(client, auth_headers, text_pdf(WORDING), name="w.pdf")
    pid = _policies(client, auth_headers)[0]["id"]
    hits = client.get(f"/api/policies/{pid}/search", params={"q": "is knee replacement covered"}, headers=auth_headers).json()
    assert hits[0]["clause"]["ref"] == "4.2" and 0 < hits[0]["score"] <= 1
    assert client.get(f"/api/policies/{pid}/search", params={"q": ""}, headers=auth_headers).status_code == 422


def test_ai_mode_adds_explanations(client, auth_headers, monkeypatch):
    def respond(schema, prompt):
        if schema is PolicyTerms:
            return PolicyTerms(policy_name="Suraksha Health Plus", insurer="Navjeevan General Insurance Company Limited", category="health")
        refs = [r for r in ("1", "2.1", "4.1", "4.2", "5") if f'ref="{r}"' in prompt]
        return ClauseLabels(items=[ClauseLabel(ref=r, category="coverage", plain_en=f"Plain {r}", plain_hi=f"सरल {r}", plain_hn=f"Simple {r}") for r in refs])

    monkeypatch.setattr("app.understanding.pipeline.get_ai", lambda: FakeAI(respond))
    upload(client, auth_headers, text_pdf(WORDING), name="w.pdf")
    p = _policies(client, auth_headers)[0]
    assert p["analysis_mode"] == "ai"
    clause = client.get(f"/api/policies/{p['id']}/clauses", headers=auth_headers).json()[3]
    assert clause["plain"] == {"en": "Plain 4.2", "hi": "सरल 4.2", "hn": "Simple 4.2"}


def test_reanalyze_and_privacy(client, db_session, auth_headers):
    upload(client, auth_headers, text_pdf(WORDING), name="w.pdf")
    pid = _policies(client, auth_headers)[0]["id"]
    r = client.post(f"/api/policies/{pid}/analyze", headers=auth_headers)
    assert r.status_code == 202
    assert client.get(f"/api/policies/{pid}", headers=auth_headers).json()["analysis_status"] == "ready"
    seed(db_session)
    demo = demo_headers(client)
    for path in ("", "/clauses", "/search?q=knee"):
        assert client.get(f"/api/policies/{pid}{path}", headers=demo).status_code == 404
    assert client.post(f"/api/policies/{pid}/analyze", headers=demo).status_code == 404


def test_suggest_kind():
    assert suggest_kind("Subject: Repudiation of claim CLM-1") == "rejection_letter"
    assert suggest_kind("Policy Schedule\nPolicy number X") == "policy_schedule"
    assert suggest_kind("Health Policy Wording\n1. Preamble") == "policy_wording"
    assert suggest_kind("DISCHARGE SUMMARY\nPatient: R") == "discharge_summary"
    assert suggest_kind("Renewal Premium Receipt No 55") == "renewal_receipt"
    assert suggest_kind("Hello world") is None
    # A wording whose preamble mentions "the Policy Schedule" is still a wording
    wording = "Suraksha Health Plus - Policy Wording\nNavjeevan General Insurance\n1. Preamble\nThe Policy Schedule, the proposal form and any endorsements form part of this Policy."
    assert suggest_kind(wording) == "policy_wording"
    # ...and a schedule that refers to the wording is still a schedule
    assert suggest_kind("Policy Schedule\nSuraksha Health Plus\nThis schedule must be read with the Policy Wording.") == "policy_schedule"


def test_real_sample_documents_are_recognised():
    from pathlib import Path

    from app.extraction import extract

    samples = Path(__file__).resolve().parents[2] / "samples"
    expected = {
        "suraksha-health-plus-policy-wording.pdf": "policy_wording",
        "suraksha-health-plus-policy-schedule.pdf": "policy_schedule",
        "drivesure-comprehensive-policy-wording.pdf": "policy_wording",
        "arogya-secure-gold-policy-wording.pdf": "policy_wording",
        "arogya-secure-gold-policy-schedule.pdf": "policy_schedule",
    }
    for name, kind in expected.items():
        if (samples / name).exists():
            text = "\n\n".join(p.text for p in extract((samples / name).read_bytes(), "application/pdf"))
            assert suggest_kind(text) == kind, name
