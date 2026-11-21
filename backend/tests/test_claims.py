from pathlib import Path

import pytest

from app.understanding.ask import ClauseView
from app.understanding.claims import InsurerReason, LetterFacts, ReasonVerdict, basic_letter_facts, check_claim, periods_from_receipts

from .fake_ai import FakeAI
from .test_documents import upload

SAMPLES = Path(__file__).resolve().parents[2] / "samples"
needs_samples = pytest.mark.skipif(not (SAMPLES / "rejection-letter-CLM-26-08817-photo.jpg").exists(), reason="run scripts/make_sample_docs.py first")

LETTER = """Navjeevan General Insurance Company Limited
Date: 03 Oct 2026
Subject: Repudiation of claim CLM-26-08817
Policy number: NGI/HL/2026/448812
Patient: Rohit Sharma
Hospital: Sample Multispeciality Hospital, Bengaluru
Date of admission: 14 Sep 2026
Claimed amount: Rs. 1,80,000
We have reviewed your claim for left total knee replacement surgery. We regret to inform you that the claim is not payable.
Reason: The treatment falls within the 24-month waiting period for joint replacement surgery under Clause 4.2 of the policy wording. The current policy commenced on 12Mar 2026 and the date of admission is within 24 months of the policy start date. If you are not satisfied with this decision, you may write to our Grievance Officer within 30 days."""

CLAUSE_42 = ClauseView(1, "4.2", "Specified illnesses and procedures", "Waiting periods",
                       "Joint replacement surgery, including knee replacement, is payable only after 24 months of Continuous Coverage from the First Policy Date. The 24 months are counted from the First Policy Date and not from the start of the current Policy Period.",
                       "waiting_period", None, None)
CLAUSE_5 = ClauseView(2, "5", "What is not covered", "What is not covered", "The Company will not pay for: 1. Cosmetic surgery. 2. Dental treatment unless an Accident.", "exclusion", None, None)


def terms(history_years=range(2022, 2027), first="2022-03-12"):
    return {
        "first_policy_date": first, "policy_start": "2026-03-12", "policy_end": "2027-03-11",
        "policy_history": [{"policy_number": None, "start": f"{y}-03-12", "end": f"{y + 1}-03-11"} for y in history_years],
        "waiting_periods": [{"name": "Specified illnesses", "months": 24, "applies_to": "joint replacement", "counted_from": "first_policy_date", "clause_ref": "4.2"}],
    }


def test_read_letter_with_rules():
    f = basic_letter_facts(LETTER)
    assert (f.claim_number, f.policy_number, f.patient) == ("CLM-26-08817", "NGI/HL/2026/448812", "Rohit Sharma")
    assert (f.admission_date, f.letter_date, f.claimed_amount) == ("2026-09-14", "2026-10-03", 180000)
    assert f.treatment == "left total knee replacement"
    [r] = f.reasons
    assert (r.type, r.clause_ref, r.insurer_counted_from) == ("waiting_period", "4.2", "2026-03-12")
    assert r.text.endswith("policy start date.")  # stops before the sign-off


def test_demo_case_insurer_counted_from_the_wrong_date():
    facts, findings, mode = check_claim(LETTER, {}, terms(), [CLAUSE_42, CLAUSE_5], True, "en", None)
    assert mode == "basic" and findings["assessment"] == "inconsistency"
    [row] = findings["rows"]
    assert (row["status"], row["code"], row["clause_ref"]) == ("contradicted", "waiting_over_counted_wrongly", "4.2")
    d = row["data"]
    assert (d["policy_start_for_waiting"], d["waiting_ends"], d["insurer_counted_from"], d["insurer_waiting_ends"]) == ("2022-03-12", "2024-03-12", "2026-03-12", "2028-03-12")
    assert row["policy_quote"]["quote"].startswith("The 24 months are counted from the First Policy Date")
    assert "12 Mar 2022" in row["question_en"] and "Why was it counted from 12 Mar 2026" in row["question_en"]
    kinds = [e["kind"] for e in findings["timeline"]]
    assert kinds[0] == "first_policy" and kinds[-2:] == ["admission", "rejection"] and "waiting_ends" in kinds and "insurer_start" in kinds
    assert {c["item"]: c["have"] for c in findings["checklist"]}["policy_history"] is True


def test_insurer_is_right_after_a_break_in_cover():
    t = terms(history_years=[2022, 2023])  # 2022-2024, then nothing until the 2026 policy
    t["policy_history"].append({"policy_number": None, "start": "2026-03-12", "end": "2027-03-11"})
    _, findings, _ = check_claim(LETTER, {}, t, [CLAUSE_42], True, "en", None)
    row = findings["rows"][0]
    assert (row["status"], row["code"]) == ("supported", "waiting_not_over_break")
    assert findings["assessment"] == "consistent" and any(e["kind"] == "break" for e in findings["timeline"])


def test_insurer_is_right_for_a_genuinely_new_policy():
    t = terms(history_years=[2026], first="2026-03-12")
    _, findings, _ = check_claim(LETTER, {}, t, [CLAUSE_42], True, "en", None)
    assert findings["rows"][0]["status"] == "supported"


def test_renewal_receipts_fill_in_missing_years():
    receipts = ["Renewal premium receipt\nPolicy NGI/HL/2023/207731 period 12 Mar 2023 to 11 Mar 2024",
                "Renewal premium receipt\nNGI/HL/2024/310962 12 Mar 2024 - 11 Mar 2025"]
    assert [p.start for p in periods_from_receipts(receipts)] == ["2023-03-12", "2024-03-12"]
    t = terms(history_years=[2022, 2025, 2026])  # 2023 and 2024 missing from the schedule: looks like a break
    _, findings, _ = check_claim(LETTER, {"renewal_receipt": receipts}, t, [CLAUSE_42], True, "en", None)
    assert findings["rows"][0]["status"] == "contradicted" and findings["policy"]["periods"] == 5


def test_other_reasons_use_ai_and_stay_unclear_without_it():
    letter = LETTER.replace("Reason: The treatment falls within the 24-month waiting period for joint replacement surgery under Clause 4.2 of the policy wording. The current policy commenced on 12Mar 2026 and the date of admission is within 24 months of the policy start date.",
                            "Reason: Dental treatment is excluded under Clause 5 of the policy.")
    _, findings, mode = check_claim(letter, {}, terms(), [CLAUSE_42, CLAUSE_5], True, "en", None)
    row = findings["rows"][0]
    assert (row["type"], row["status"], row["clause_ref"], mode) == ("exclusion", "unclear", "5", "basic")
    assert findings["assessment"] == "needs_info" and row["question_en"]

    def respond(schema, prompt):
        if schema is LetterFacts:
            return LetterFacts(claim_number="CLM-1", admission_date="2026-09-14", reasons=[InsurerReason(type="exclusion", text="Dental treatment is excluded", clause_ref="5")])
        assert 'ref="5"' in prompt and "Hinglish" in prompt
        return ReasonVerdict(status="supported", policy_says_en="Dental treatment is excluded unless an accident.", explanation_en="The clause excludes it.",
                             explanation_local="Clause ise exclude karta hai.", question_en="Was it due to an accident?", question_local="Kya accident tha?", evidence_needed=["dentist's note"])

    _, findings, mode = check_claim(letter, {}, terms(), [CLAUSE_42, CLAUSE_5], True, "hn", FakeAI(respond))
    row = findings["rows"][0]
    assert mode == "ai" and row["status"] == "supported" and row["explanation_local"] == "Clause ise exclude karta hai."
    assert findings["questions"] == [{"en": "Was it due to an accident?", "local": "Kya accident tha?"}]


# ---------- the whole flow through the API, with the real sample documents ----------

@needs_samples
def test_rejection_check_end_to_end(client, auth_headers, isolated_storage):
    for name, kind in [("suraksha-health-plus-policy-wording.pdf", "policy_wording"), ("suraksha-health-plus-policy-schedule.pdf", "policy_schedule")]:
        upload(client, auth_headers, (SAMPLES / name).read_bytes(), name=name, kind=kind)
    policy = client.get("/api/policies", headers=auth_headers).json()[0]
    analysed_at = policy["analyzed_at"]

    claim = client.post("/api/claims", json={"policy_id": policy["id"]}, headers=auth_headers).json()
    assert claim["status"] == "draft"
    assert client.post(f"/api/claims/{claim['id']}/check", json={}, headers=auth_headers).json()["detail"] == "no_letter"

    letter = upload(client, auth_headers, (SAMPLES / "rejection-letter-CLM-26-08817-photo.jpg").read_bytes(), name="letter.jpg", kind="rejection_letter")
    assert letter.status_code == 201
    client.patch(f"/api/documents/{letter.json()['id']}", json={"claim_id": claim["id"]}, headers=auth_headers)
    # a claim document must not make the policy be read again
    assert client.get(f"/api/policies/{policy['id']}", headers=auth_headers).json()["analyzed_at"] == analysed_at

    r = client.post(f"/api/claims/{claim['id']}/check", json={"lang": "hi"}, headers=auth_headers)
    assert r.status_code == 202
    claim = client.get(f"/api/claims/{claim['id']}", headers=auth_headers).json()
    assert claim["status"] == "ready" and claim["lang"] == "hi"
    assert claim["facts"]["claim_number"] == "CLM-26-08817" and claim["facts"]["admission_date"] == "2026-09-14"
    assert claim["findings"]["assessment"] == "inconsistency"
    row = claim["findings"]["rows"][0]
    assert row["status"] == "contradicted" and row["data"]["waiting_ends"] == "2024-03-12" and row["data"]["insurer_counted_from"] == "2026-03-12"

    pdf = client.get(f"/api/claims/{claim['id']}/report", headers=auth_headers)
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF") and "CLM-26-08817" in pdf.headers["content-disposition"]
    import pymupdf

    text = " ".join("".join(p.get_text() for p in pymupdf.open(stream=pdf.content, filetype="pdf")).split())  # ignore line wrapping
    assert "Possible inconsistency found" in text and "12 Mar 2024" in text and "Why was it counted from 12 Mar 2026" in text

    assert len(client.get(f"/api/documents?claim_id={claim['id']}", headers=auth_headers).json()) == 1
    assert client.delete(f"/api/claims/{claim['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/documents/{letter.json()['id']}", headers=auth_headers).status_code == 404


@needs_samples
def test_claim_finds_its_policy_by_number(client, auth_headers):
    upload(client, auth_headers, (SAMPLES / "suraksha-health-plus-policy-schedule.pdf").read_bytes(), name="s.pdf", kind="policy_schedule")
    upload(client, auth_headers, (SAMPLES / "suraksha-health-plus-policy-wording.pdf").read_bytes(), name="w.pdf", kind="policy_wording")
    pid = client.get("/api/policies", headers=auth_headers).json()[0]["id"]
    claim = client.post("/api/claims", json={}, headers=auth_headers).json()
    upload_r = client.post("/api/documents", headers=auth_headers, data={"kind": "rejection_letter", "claim_id": str(claim["id"])},
                           files={"file": ("l.jpg", (SAMPLES / "rejection-letter-CLM-26-08817-photo.jpg").read_bytes(), "image/jpeg")})
    assert upload_r.json()["claim_id"] == claim["id"]
    client.post(f"/api/claims/{claim['id']}/check", json={}, headers=auth_headers)
    claim = client.get(f"/api/claims/{claim['id']}", headers=auth_headers).json()
    assert claim["policy_id"] == pid and claim["findings"]["assessment"] == "inconsistency"


def test_claims_are_private(client, db_session, auth_headers):
    from app.seed import seed

    from .test_documents import demo_headers

    claim = client.post("/api/claims", json={}, headers=auth_headers).json()
    seed(db_session)
    demo = demo_headers(client)
    for method, path in [("get", ""), ("post", "/check"), ("get", "/report"), ("delete", "")]:
        r = getattr(client, method)(f"/api/claims/{claim['id']}{path}", headers=demo, **({"json": {}} if method == "post" else {}))
        assert r.status_code == 404, (method, path)
    assert client.get("/api/claims", headers=demo).json() == []
    demo_policy = client.get("/api/policies", headers=demo).json()[0]["id"]
    assert client.post("/api/claims", json={"policy_id": demo_policy}, headers=auth_headers).status_code == 404
