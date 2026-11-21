"""Continuous cover and waiting-period end dates.

Waiting periods are counted from whatever the policy wording says (usually the First Policy
Date, provided cover has been continuous). A renewal counts as continuous if the next policy
starts no later than the grace period after the previous one ended.
"""

import calendar
from dataclasses import asdict, dataclass, field
from datetime import date

from ..understanding.dates import parse_date
from ..understanding.terms import PolicyTerms, WaitingPeriod

GRACE_DAYS = 30


def add_months(d: date, months: int) -> date:
    """12 Mar 2022 + 24 months = 12 Mar 2024; 31 Jan + 1 month = 28/29 Feb."""
    month_index = d.month - 1 + months
    year, month = d.year + month_index // 12, month_index % 12 + 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


@dataclass
class CoverBreak:
    previous_end: str
    next_start: str
    gap_days: int


@dataclass
class ContinuousCover:
    continuous_since: str | None  # start of the latest unbroken run of policies
    breaks: list[CoverBreak] = field(default_factory=list)
    periods_checked: int = 0


def continuous_cover(terms: PolicyTerms, grace_days: int = GRACE_DAYS) -> ContinuousCover:
    periods = sorted(
        ((parse_date(p.start), parse_date(p.end)) for p in terms.policy_history),
        key=lambda p: p[0] or date.min,
    )
    periods = [(s, e) for s, e in periods if s and e]
    if not periods:
        return ContinuousCover(continuous_since=terms.first_policy_date)

    breaks: list[CoverBreak] = []
    since = periods[0][0]
    for (_, prev_end), (next_start, _) in zip(periods, periods[1:]):
        gap = (next_start - prev_end).days - 1  # 11 Mar -> 12 Mar is no gap
        if gap > grace_days:
            breaks.append(CoverBreak(prev_end.isoformat(), next_start.isoformat(), gap))
            since = next_start
    # The schedule's First Policy Date is the insurer's own record; trust it when the history
    # we have starts later (older policies simply weren't uploaded) and shows no break.
    first = parse_date(terms.first_policy_date)
    if not breaks and first and first < since:
        since = first
    return ContinuousCover(continuous_since=since.isoformat(), breaks=breaks, periods_checked=len(periods))


@dataclass
class WaitingStatus:
    name: str
    clause_ref: str | None
    months: int
    counted_from: str  # first_policy_date | policy_start | unclear
    starts: str | None  # the date the period is counted from
    ends: str | None  # first day the treatment is covered
    completed: bool | None  # as of `today`; None when dates are missing
    days_left: int | None
    note: str | None = None  # machine-readable flag: "break_in_cover", "basis_unclear", "missing_dates"

    def to_dict(self) -> dict:
        return asdict(self)


def waiting_status(wp: WaitingPeriod, terms: PolicyTerms, today: date | None = None) -> WaitingStatus:
    today = today or date.today()
    cover = continuous_cover(terms)
    note = None
    if wp.counted_from == "policy_start":
        start = parse_date(terms.policy_start)
    else:
        start = parse_date(cover.continuous_since) or parse_date(terms.policy_start)
        if wp.counted_from == "unclear":
            note = "basis_unclear"
        elif cover.breaks:
            note = "break_in_cover"
    if start is None:
        return WaitingStatus(wp.name, wp.clause_ref, wp.months, wp.counted_from, None, None, None, None, "missing_dates")
    ends = add_months(start, wp.months)
    return WaitingStatus(
        name=wp.name,
        clause_ref=wp.clause_ref,
        months=wp.months,
        counted_from=wp.counted_from,
        starts=start.isoformat(),
        ends=ends.isoformat(),
        completed=today >= ends,
        days_left=max(0, (ends - today).days),
        note=note,
    )


def covered_on(status: WaitingStatus, event: date) -> bool | None:
    """Had the waiting period ended by `event` (e.g. the date of admission)?"""
    ends = parse_date(status.ends)
    return None if ends is None else event >= ends


def policy_timeline(terms: PolicyTerms, today: date | None = None) -> dict:
    """Everything the UI needs about dates: continuous cover and each waiting period."""
    cover = continuous_cover(terms)
    return {
        "continuous_since": cover.continuous_since,
        "breaks": [asdict(b) for b in cover.breaks],
        "periods_checked": cover.periods_checked,
        "waiting_periods": [waiting_status(wp, terms, today).to_dict() for wp in terms.waiting_periods],
    }
