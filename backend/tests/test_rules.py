from datetime import date

import pytest

from app.rules.coverage import add_months, continuous_cover, covered_on, policy_timeline, waiting_status
from app.understanding.terms import PolicyPeriod, PolicyTerms, WaitingPeriod

JOINT = WaitingPeriod(name="Specified illnesses", months=24, applies_to="joint replacement", counted_from="first_policy_date", clause_ref="4.2")


def rohit(**over) -> PolicyTerms:
    """The demo case: yearly renewals since 12 Mar 2022, no breaks."""
    history = [PolicyPeriod(policy_number=f"P{y}", start=f"{y}-03-12", end=f"{y + 1}-03-11") for y in range(2022, 2027)]
    base = dict(first_policy_date="2022-03-12", policy_start="2026-03-12", policy_end="2027-03-11", policy_history=history, waiting_periods=[JOINT])
    return PolicyTerms(**{**base, **over})


@pytest.mark.parametrize(
    "d,n,expected",
    [(date(2022, 3, 12), 24, date(2024, 3, 12)), (date(2024, 1, 31), 1, date(2024, 2, 29)), (date(2023, 1, 31), 1, date(2023, 2, 28)),
     (date(2023, 11, 15), 3, date(2024, 2, 15)), (date(2024, 2, 29), 12, date(2025, 2, 28))],
)
def test_add_months(d, n, expected):
    assert add_months(d, n) == expected


def test_continuous_cover_without_breaks():
    cover = continuous_cover(rohit())
    assert cover.continuous_since == "2022-03-12" and cover.breaks == [] and cover.periods_checked == 5


def test_late_renewal_within_grace_is_still_continuous():
    t = rohit()
    t.policy_history[2] = PolicyPeriod(start="2024-04-05", end="2025-04-04")  # 24 days late
    t.policy_history[3] = PolicyPeriod(start="2025-04-05", end="2026-04-04")
    t.policy_history[4] = PolicyPeriod(start="2026-04-05", end="2027-04-04")
    assert continuous_cover(t).breaks == []


def test_break_restarts_continuous_cover():
    t = rohit()
    t.policy_history[2] = PolicyPeriod(start="2024-06-01", end="2025-05-31")  # 81-day gap after 11 Mar 2024
    t.policy_history[3] = PolicyPeriod(start="2025-06-01", end="2026-05-31")
    t.policy_history[4] = PolicyPeriod(start="2026-06-01", end="2027-05-31")
    cover = continuous_cover(t)
    assert cover.continuous_since == "2024-06-01"
    assert cover.breaks[0].gap_days == 81
    status = waiting_status(JOINT, t, today=date(2026, 9, 14))
    assert (status.starts, status.ends, status.note) == ("2024-06-01", "2026-06-01", "break_in_cover")


def test_first_policy_date_used_when_older_policies_not_uploaded():
    t = rohit(policy_history=[PolicyPeriod(start="2026-03-12", end="2027-03-11")])
    assert continuous_cover(t).continuous_since == "2022-03-12"


def test_demo_case_waiting_period_ended_long_before_surgery():
    status = waiting_status(JOINT, rohit(), today=date(2026, 11, 20))
    assert (status.starts, status.ends, status.completed, status.days_left) == ("2022-03-12", "2024-03-12", True, 0)
    # Admission on 14 Sep 2026: covered, even though it is within 24 months of the latest renewal
    assert covered_on(status, date(2026, 9, 14)) is True


def test_waiting_period_counted_from_policy_start():
    wp = JOINT.model_copy(update={"counted_from": "policy_start"})
    status = waiting_status(wp, rohit(), today=date(2026, 11, 20))
    assert (status.starts, status.ends, status.completed) == ("2026-03-12", "2028-03-12", False)
    assert status.days_left == (date(2028, 3, 12) - date(2026, 11, 20)).days
    assert covered_on(status, date(2026, 9, 14)) is False


def test_unclear_basis_is_flagged():
    wp = JOINT.model_copy(update={"counted_from": "unclear"})
    assert waiting_status(wp, rohit()).note == "basis_unclear"


def test_missing_dates():
    status = waiting_status(JOINT, PolicyTerms())
    assert status.note == "missing_dates" and status.ends is None and covered_on(status, date(2026, 1, 1)) is None


def test_policy_timeline_bundle():
    tl = policy_timeline(rohit(), today=date(2026, 11, 20))
    assert tl["continuous_since"] == "2022-03-12" and tl["breaks"] == []
    assert tl["waiting_periods"][0]["ends"] == "2024-03-12"
