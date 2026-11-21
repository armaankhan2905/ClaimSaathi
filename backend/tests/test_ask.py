from datetime import date

import pytest

from app.ai import AIError
from app.understanding.ask import AskAnswer, Citation, ClauseView, answer_question, best_sentence, facts_text, retrieval_query

from .doc_factory import text_pdf
from .fake_ai import FakeAI
from .test_documents import upload
from .test_pipeline import SCHEDULE, WORDING

CLAUSES = [
    ClauseView(1, "3.2", "Room, boarding and nursing", "What is covered", "Room rent is payable up to 1% of the Sum Insured per day. ICU up to 2%.", "limit", {"en": "Room up to 1% a day.", "hi": "कमरा 1% प्रति दिन तक।", "hn": "Room 1% per day tak."}, None),
    ClauseView(2, "4.2", "Specified illnesses and procedures", "Waiting periods", "Joint replacement surgery, including knee replacement, is payable only after 24 months of Continuous Coverage from the First Policy Date.", "waiting_period", None, None),
    ClauseView(3, "9", "Grievances", "Grievances", "Write to the Grievance Officer. You may approach the Insurance Ombudsman within one year.", "grievance", None, None),
]
TERMS = {
    "first_policy_date": "2022-03-12", "policy_start": "2026-03-12", "policy_end": "2027-03-11", "sum_insured": 500000,
    "policy_history": [{"policy_number": None, "start": f"{y}-03-12", "end": f"{y + 1}-03-11"} for y in range(2022, 2027)],
    "waiting_periods": [{"name": "Specified illnesses", "months": 24, "applies_to": "knee", "counted_from": "first_policy_date", "clause_ref": "4.2"}],
}


def test_facts_include_exact_waiting_period_dates():
    facts = facts_text(TERMS, today=date(2026, 11, 21))
    assert "Continuous cover with this insurer since: 2022-03-12" in facts
    assert "clause 4.2): 24 months counted from 2022-03-12" in facts and "ends 2024-03-12: already over" in facts
    assert "Today's date: 2026-11-21" in facts


def test_short_follow_up_is_searched_with_previous_question():
    history = [{"role": "user", "content": "Is knee replacement covered?"}, {"role": "assistant", "content": "Yes after 24 months."}]
    assert retrieval_query("and cataract?", history) == "Is knee replacement covered? and cataract?"
    assert retrieval_query("What is the room rent limit for ICU stays?", history) == "What is the room rent limit for ICU stays?"


def test_new_short_question_is_not_drowned_out_by_previous_topic():
    from app.understanding.ask import gather_clauses

    history = [{"role": "user", "content": "How much room rent per day can I claim?"}]
    found = [c.ref for c in gather_clauses("ombudsman complaint?", history, CLAUSES, k=3)]
    assert found[0] == "9"  # the question's own best match leads
    found = [c.ref for c in gather_clauses("and knee?", history, CLAUSES, k=3)]
    assert found[0] == "4.2" and "3.2" in found  # follow-up keeps the previous topic in reach


def test_best_sentence_picks_matching_sentence():
    text = "Room rent is limited. Knee replacement is payable after 24 months. Ambulance up to Rs. 2,000."
    assert best_sentence(text, "knee surgery months") == "Knee replacement is payable after 24 months."


def test_basic_mode_returns_matching_clauses():
    r = answer_question("Is knee replacement covered?", "hi", CLAUSES, TERMS, [], None)
    assert r.answer_type == "search_only" and r.mode == "basic"
    assert r.citations[0]["ref"] == "4.2"
    r = answer_question("room rent per day", "hi", CLAUSES, TERMS, [], None)
    assert r.citations[0] == {"ref": "3.2", "title": "Room, boarding and nursing", "quote": "कमरा 1% प्रति दिन तक।", "clause_id": 1}


def test_question_nothing_matches():
    r = answer_question("xyzzy plugh", "en", CLAUSES, TERMS, [], None)
    assert r.answer_type == "not_in_policy" and r.citations == []


def test_ai_answer_with_verified_citations():
    calls = []

    def respond(schema, prompt):
        calls.append(prompt)
        return AskAnswer(
            answer_type="answered",
            answer="Haan, knee replacement ka 24 months ka waiting period 12 Mar 2024 ko khatam ho chuka hai.",
            citations=[
                Citation(ref="4.2", quote="payable only after 24 months of Continuous Coverage"),  # real quote: kept
                Citation(ref="7.7", quote="made up"),  # not supplied: dropped
                Citation(ref="§3.2", quote="Room rent is free"),  # invented quote: replaced with real text
            ],
            follow_ups=["Cataract ka kya?", "", "Claim kaise karein?"],
        )

    r = answer_question("knee replacement cover hogi kya, aur room rent?", "hn", CLAUSES, TERMS, [], FakeAI(respond))
    assert r.mode == "ai" and r.answer_type == "answered" and r.answer.startswith("Haan")
    assert [c["ref"] for c in r.citations] == ["4.2", "3.2"]
    assert r.citations[0]["quote"] == "payable only after 24 months of Continuous Coverage"
    assert r.citations[1]["quote"] != "Room rent is free" and r.citations[1]["quote"] in CLAUSES[0].text
    assert r.follow_ups == ["Cataract ka kya?", "Claim kaise karein?"]
    assert "<computed_facts>" in calls[0] and "Hinglish" in calls[0] and 'ref="4.2"' in calls[0]


def test_answer_without_valid_citation_is_not_presented_as_settled():
    fake = FakeAI(lambda s, p: AskAnswer(answer_type="answered", answer="Yes.", citations=[Citation(ref="99", quote="x")], follow_ups=[]))
    assert answer_question("knee replacement?", "en", CLAUSES, TERMS, [], fake).answer_type == "needs_more_info"


def test_ai_failure_falls_back_to_matching_clauses():
    def boom(s, p):
        raise AIError("rate_limited")

    r = answer_question("knee replacement covered?", "en", CLAUSES, TERMS, [], FakeAI(boom))
    assert r.answer_type == "search_only" and r.citations[0]["ref"] == "4.2"


# ---------- API ----------

@pytest.fixture
def understood_policy(client, auth_headers):
    upload(client, auth_headers, text_pdf(WORDING), name="w.pdf")
    upload(client, auth_headers, text_pdf(SCHEDULE), name="s.pdf", kind="policy_schedule")
    return client.get("/api/policies", headers=auth_headers).json()[0]["id"]


def test_chat_api_round_trip(client, auth_headers, understood_policy):
    pid = understood_policy
    assert client.get(f"/api/policies/{pid}/chat", headers=auth_headers).json() == []
    r = client.post(f"/api/policies/{pid}/chat", json={"question": "Is knee replacement covered?", "lang": "en"}, headers=auth_headers)
    assert r.status_code == 200
    q, a = r.json()
    assert (q["role"], q["content"]) == ("user", "Is knee replacement covered?")
    assert a["role"] == "assistant" and a["answer_type"] == "search_only" and a["citations"][0]["ref"] == "4.2"
    assert len(client.get(f"/api/policies/{pid}/chat", headers=auth_headers).json()) == 2
    assert client.delete(f"/api/policies/{pid}/chat", headers=auth_headers).status_code == 204
    assert client.get(f"/api/policies/{pid}/chat", headers=auth_headers).json() == []


def test_chat_with_ai(client, auth_headers, understood_policy, monkeypatch):
    fake = FakeAI(lambda s, p: AskAnswer(answer_type="answered", answer="Covered after 24 months.", citations=[Citation(ref="4.2", quote="after 24 months")], follow_ups=["And cataract?"]))
    monkeypatch.setattr("app.routers.chat.get_ai", lambda: fake)
    a = client.post(f"/api/policies/{understood_policy}/chat", json={"question": "knee?", "lang": "en"}, headers=auth_headers).json()[1]
    assert a["mode"] == "ai" and a["content"] == "Covered after 24 months." and a["follow_ups"] == ["And cataract?"]
    assert a["citations"][0]["clause_id"]


def test_chat_validation_and_privacy(client, db_session, auth_headers, understood_policy):
    pid = understood_policy
    assert client.post(f"/api/policies/{pid}/chat", json={"question": ""}, headers=auth_headers).status_code == 422
    assert client.post(f"/api/policies/{pid}/chat", json={"question": "x", "lang": "fr"}, headers=auth_headers).status_code == 422
    from app.seed import seed

    from .test_documents import demo_headers

    seed(db_session)
    demo = demo_headers(client)
    assert client.get(f"/api/policies/{pid}/chat", headers=demo).status_code == 404
    assert client.post(f"/api/policies/{pid}/chat", json={"question": "hi"}, headers=demo).status_code == 404
    # a policy with no clauses can't be asked about yet
    demo_pid = client.get("/api/policies", headers=demo).json()[0]["id"]
    assert client.post(f"/api/policies/{demo_pid}/chat", json={"question": "hi"}, headers=demo).json()["detail"] == "no_clauses"
