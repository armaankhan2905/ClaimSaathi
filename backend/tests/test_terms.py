from datetime import date

import pytest

from app.ai import AIError
from app.understanding.clauses import split_clauses
from app.understanding.dates import parse_date
from app.understanding.labels import ClauseLabel, ClauseLabels, basic_category, label_clauses
from app.understanding.terms import PolicyTerms, WaitingPeriod, basic_terms, extract_terms

from .fake_ai import FakeAI

SCHEDULE = """Policy Schedule
Suraksha Health Plus - Navjeevan General Insurance Company Limited
Policy number NGI/HL/2026/448812
Policyholder Rohit Sharma
Policy period 12 Mar 2026 to 11 Mar 2027 (both days inclusive)
First Policy Date 12 Mar 2022
Sum Insured Rs. 5,00,000
Room rent limit 1% of Sum Insured per day (Rs. 5,000)
Co-payment 10% outside network hospitals
Premium Rs. 10,576 + GST Rs. 1,904 = Rs. 12,480
NGI/HL/2024/310962 12 Mar 2024 - 11 Mar 2025 Rs. 5,00,000
NGI/HL/2022/118204 12 Mar 2022 - 11 Mar 2023 Rs. 5,00,000"""

WORDING = """Suraksha Health Plus - Policy Wording
Navjeevan General Insurance Company Limited
2. Definitions
2.1 Grace Period
The period of 30 days after expiry during which the policy may be renewed.
4. Waiting periods
4.1 Initial waiting period
No expenses are payable for any illness contracted within the first 30 days from the First Policy Date.
4.2 Specified illnesses and procedures
Joint replacement is payable only after 24 months of Continuous Coverage from the First Policy Date.
4.3 Maternity
Payable after a waiting period of 36 months from the start of the current policy.
5. Room rent
5.1 Depreciation limit
Room rent is limited to 1% of the sum insured per day in hospitalisation."""


@pytest.mark.parametrize(
    "s,expected",
    [("12 Mar 2026", date(2026, 3, 12)), ("12-Mar-2026", date(2026, 3, 12)), ("March 12, 2026", date(2026, 3, 12)),
     ("2026-03-12", date(2026, 3, 12)), ("12/03/2026", date(2026, 3, 12)), ("31/02/2026", None), ("soon", None), (None, None)],
)
def test_parse_date(s, expected):
    assert parse_date(s) == expected


def _clauses():
    return split_clauses([(1, WORDING)])


def test_basic_terms_from_schedule_and_wording():
    t = basic_terms(SCHEDULE, WORDING, _clauses())
    assert t.policy_name == "Suraksha Health Plus"
    assert t.insurer == "Navjeevan General Insurance Company Limited"
    assert t.category == "health"
    assert (t.policy_number, t.policyholder) == ("NGI/HL/2026/448812", "Rohit Sharma")
    assert (t.policy_start, t.policy_end, t.first_policy_date) == ("2026-03-12", "2027-03-11", "2022-03-12")
    assert (t.sum_insured, t.premium) == (500000, 12480)
    assert t.room_rent_limit.startswith("1% of Sum Insured") and t.copayment.startswith("10%")
    assert [p.policy_number for p in t.policy_history] == ["NGI/HL/2022/118204", "NGI/HL/2024/310962"]  # sorted oldest first


def test_basic_waiting_periods_and_what_they_count_from():
    wps = {w.clause_ref: w for w in basic_terms(SCHEDULE, WORDING, _clauses()).waiting_periods}
    assert set(wps) == {"4.1", "4.2", "4.3"}
    assert (wps["4.2"].months, wps["4.2"].counted_from) == (24, "first_policy_date")
    assert (wps["4.1"].months, wps["4.1"].counted_from) == (1, "first_policy_date")
    assert (wps["4.3"].months, wps["4.3"].counted_from) == (36, "policy_start")


def test_basic_categories():
    cats = {c.ref: basic_category(c) for c in _clauses()}
    assert cats == {"2.1": "definition", "4.1": "waiting_period", "4.2": "waiting_period", "4.3": "waiting_period", "5.1": "limit"}


def test_ai_terms_are_used_and_gaps_filled_from_rules():
    ai_terms = PolicyTerms(
        policy_name="Suraksha Health Plus", insurer="Navjeevan General Insurance Company Limited",
        first_policy_date="not a date", sum_insured=500000, key_exclusions=["Cosmetic surgery"],
        waiting_periods=[WaitingPeriod(name="Joint replacement", months=24, applies_to="knee and hip", counted_from="first_policy_date", clause_ref="4.2")],
    )
    fake = FakeAI(lambda schema, prompt: ai_terms)
    t, mode = extract_terms(SCHEDULE, WORDING, _clauses(), fake)
    assert mode == "ai" and fake.calls[0][0] == "PolicyTerms"
    assert "<policy_schedule>" in fake.calls[0][1] and "4.2 Specified illnesses" in fake.calls[0][1]
    assert t.key_exclusions == ["Cosmetic surgery"]  # from AI
    assert len(t.waiting_periods) == 1  # AI list kept as is
    assert t.policy_number == "NGI/HL/2026/448812"  # gap filled by rules
    assert t.first_policy_date == "2022-03-12"  # unparseable AI date replaced


def test_ai_failure_falls_back_to_basic():
    def boom(schema, prompt):
        raise AIError("connection")

    t, mode = extract_terms(SCHEDULE, WORDING, _clauses(), FakeAI(boom))
    assert mode == "basic" and t.sum_insured == 500000


def test_label_clauses_with_ai_in_batches():
    clauses = _clauses()

    def respond(schema, prompt):
        refs = [c.ref for c in clauses if f'ref="{c.ref}"' in prompt]
        return ClauseLabels(items=[ClauseLabel(ref=r, category="coverage", plain_en=f"en {r}", plain_hi=f"hi {r}", plain_hn=f"hn {r}") for r in refs if r != "5.1"])

    fake = FakeAI(respond)
    labels, mode = label_clauses(clauses, fake)
    assert mode == "ai"
    assert labels[0] == ("coverage", {"en": "en 2.1", "hi": "hi 2.1", "hn": "hn 2.1"})
    assert labels[-1] == ("limit", None)  # the model skipped 5.1: rule-based category kept


def test_label_clauses_basic_mode():
    labels, mode = label_clauses(_clauses(), None)
    assert mode == "basic" and all(plain is None for _, plain in labels)
