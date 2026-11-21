from pathlib import Path

import pytest

from app.understanding.compare import PolicyVerdict, ScenarioCitation, month_from_text

from .fake_ai import FakeAI
from .test_documents import upload

SAMPLES = Path(__file__).resolve().parents[2] / "samples"
pytestmark = pytest.mark.skipif(not (SAMPLES / "arogya-secure-gold-policy-wording.pdf").exists(), reason="run scripts/make_sample_docs.py first")


@pytest.fixture
def two_policies(client, auth_headers):
    """Suraksha (knee 24 months, PED 36, maternity after 36) and Arogya (knee 36, PED 24, no maternity)."""
    for name, kind in [
        ("suraksha-health-plus-policy-wording.pdf", "policy_wording"),
        ("suraksha-health-plus-policy-schedule.pdf", "policy_schedule"),
        ("arogya-secure-gold-policy-wording.pdf", "policy_wording"),
        ("arogya-secure-gold-policy-schedule.pdf", "policy_schedule"),
    ]:
        upload(client, auth_headers, (SAMPLES / name).read_bytes(), name=name, kind=kind)
    ids = {p["name"]: p["id"] for p in client.get("/api/policies", headers=auth_headers).json()}
    assert set(ids) == {"Suraksha Health Plus", "Arogya Secure Gold"}
    return ids["Suraksha Health Plus"], ids["Arogya Secure Gold"]


def _run(client, headers, a, b, **body):
    r = client.post("/api/compare", json={"a": a, "b": b, "lang": "en", **body}, headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


@pytest.mark.parametrize("text,month", [("knee surgery in the 3rd year", 30), ("year 2", 18), ("after 20 months", 20), ("dusre saal mein", None), ("3 saal baad", 30), ("no timing", None)])
def test_month_from_text(text, month):
    assert month_from_text(text) == month


def test_basic_mode_knee_replacement_in_year_3(client, auth_headers, two_policies):
    s, a = two_policies
    r = _run(client, auth_headers, s, a, scenario="knee_year3")
    assert r["scenario"]["month"] == 30
    assert r["a"]["verdict"] == "covered" and r["a"]["reason"] == {"code": "waiting_over", "months": 24}
    assert r["b"]["verdict"] == "not_covered" and r["b"]["reason"] == {"code": "waiting_not_over", "months": 36}
    assert r["b"]["citations"][0]["ref"] == "4.2"
    assert r["winner"] == "a"


def test_basic_mode_pre_existing_diabetes_in_year_3_goes_the_other_way(client, auth_headers, two_policies):
    s, a = two_policies
    r = _run(client, auth_headers, s, a, scenario="diabetes_year3")
    assert r["a"]["verdict"] == "not_covered" and r["a"]["reason"]["months"] == 36
    assert r["b"]["verdict"] == "covered" and r["winner"] == "b"


def test_basic_mode_maternity(client, auth_headers, two_policies):
    s, a = two_policies
    r = _run(client, auth_headers, s, a, scenario="maternity_year2")
    assert r["a"]["verdict"] == "not_covered" and r["a"]["reason"]["code"] == "waiting_not_over"
    assert r["b"]["verdict"] == "not_covered" and r["b"]["reason"]["code"] == "excluded"


def test_feature_table(client, auth_headers, two_policies):
    s, a = two_policies
    rows = {r["key"]: r for r in client.get(f"/api/compare/table?a={s}&b={a}", headers=auth_headers).json()}
    assert rows["premium"] == {"key": "premium", "a": 12480, "b": 14860, "better": "a"}
    assert rows["wait_specified"]["a"] == 24 and rows["wait_specified"]["b"] == 36 and rows["wait_specified"]["better"] == "a"
    assert rows["wait_ped"]["better"] == "b"
    assert rows["room_rent"]["better"] == "b" and rows["copay"]["better"] == "b"
    assert rows["maternity"] == {"key": "maternity", "a": "covered", "b": "not_covered", "better": "a"}


def test_ai_verdicts_are_cached_and_citations_checked(client, auth_headers, two_policies, monkeypatch):
    s, a = two_policies
    calls = []

    def respond(schema, prompt):
        calls.append(prompt)
        assert "month 30 of holding the policy" in prompt
        assert "(NOT over by then)" in prompt or "(already over by then)" in prompt
        return PolicyVerdict(verdict="covered", summary="Covered.", what_you_pay="", citations=[ScenarioCitation(ref="4.2", quote="invented words"), ScenarioCitation(ref="99", quote="x")])

    monkeypatch.setattr("app.routers.compare.get_ai", lambda: FakeAI(respond))
    r1 = _run(client, auth_headers, s, a, scenario="knee_year3", lang="hi")
    assert r1["a"]["mode"] == "ai" and [c["ref"] for c in r1["a"]["citations"]] == ["4.2"]
    assert r1["a"]["citations"][0]["quote"] != "invented words"  # replaced with real clause text
    assert "Hindi" in calls[0]
    r2 = _run(client, auth_headers, s, a, scenario="knee_year3", lang="hi")
    assert r2 == r1 and len(calls) == 2  # second run served from cache (2 calls = one per policy)


def test_custom_scenario_and_errors(client, auth_headers, two_policies):
    s, a = two_policies
    r = _run(client, auth_headers, s, a, custom="cataract operation in the 4th year")
    assert r["scenario"]["key"] is None and r["scenario"]["month"] == 42
    assert client.post("/api/compare", json={"a": s, "b": s, "scenario": "knee_year3"}, headers=auth_headers).json()["detail"] == "same_policy"
    assert client.post("/api/compare", json={"a": s, "b": a, "scenario": "nope"}, headers=auth_headers).status_code == 404
    assert client.post("/api/compare", json={"a": s, "b": a}, headers=auth_headers).status_code == 422
    scen = client.get("/api/compare/scenarios?category=motor").json()
    assert {x["key"] for x in scen} == {"flood_engine", "bumper_zero_dep", "no_licence"}


def test_compare_is_private(client, db_session, auth_headers, two_policies):
    from app.seed import seed

    from .test_documents import demo_headers

    seed(db_session)
    s, a = two_policies
    demo = demo_headers(client)
    assert client.post("/api/compare", json={"a": s, "b": a, "scenario": "knee_year3"}, headers=demo).status_code == 404
    assert client.get(f"/api/compare/table?a={s}&b={a}", headers=demo).status_code == 404
