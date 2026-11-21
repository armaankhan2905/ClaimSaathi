"""Key policy terms: who, what, how much, when, and the waiting periods.

`extract_terms` asks Claude when available and always runs the rule-based reader too:
the rules fill anything the AI left empty, and are the whole answer in basic mode.
"""

import logging
import re
from typing import Literal

from pydantic import BaseModel, Field

from ..ai import AIClientProtocol, AIError
from .clauses import SplitClause
from .dates import DATE_PATTERN, iso, parse_date

log = logging.getLogger(__name__)

CountedFrom = Literal["first_policy_date", "policy_start", "unclear"]


class WaitingPeriod(BaseModel):
    name: str = Field(description="Short name, e.g. 'Specified illnesses and procedures'")
    months: int = Field(description="Length of the waiting period in months (30 days = 1 month)")
    applies_to: str = Field(description="What it applies to, in a few words, e.g. 'joint replacement, cataract, hernia'")
    counted_from: CountedFrom = Field(description="What the policy wording says the period is counted from")
    clause_ref: str | None = Field(default=None, description="Clause number it comes from, e.g. '4.2'")


class PolicyPeriod(BaseModel):
    policy_number: str | None = None
    start: str | None = Field(default=None, description="YYYY-MM-DD")
    end: str | None = Field(default=None, description="YYYY-MM-DD")


class PolicyTerms(BaseModel):
    policy_name: str | None = Field(default=None, description="Product name, e.g. 'Suraksha Health Plus'")
    insurer: str | None = None
    category: Literal["health", "motor", "life", "travel", "other"] | None = None
    policy_number: str | None = None
    policyholder: str | None = None
    policy_start: str | None = Field(default=None, description="Start of the current policy period, YYYY-MM-DD")
    policy_end: str | None = Field(default=None, description="End of the current policy period, YYYY-MM-DD")
    first_policy_date: str | None = Field(default=None, description="Start of continuous cover with this insurer, YYYY-MM-DD")
    sum_insured: int | None = Field(default=None, description="In rupees (IDV for motor policies)")
    premium: int | None = Field(default=None, description="Total premium in rupees including tax")
    room_rent_limit: str | None = Field(default=None, description="As stated, e.g. '1% of sum insured per day'")
    icu_limit: str | None = None
    copayment: str | None = Field(default=None, description="As stated, e.g. '10% outside network hospitals'")
    waiting_periods: list[WaitingPeriod] = Field(default_factory=list)
    policy_history: list[PolicyPeriod] = Field(default_factory=list, description="Earlier and current policy periods, oldest first")
    addons: list[str] = Field(default_factory=list)
    key_exclusions: list[str] = Field(default_factory=list, description="Up to 8 most important exclusions, a few words each")


TERMS_SYSTEM = """You read Indian insurance policy documents and extract key terms exactly as written.
Rules:
- Use only what the documents say. Leave a field null (or a list empty) when it isn't stated. Never guess.
- Dates as YYYY-MM-DD. Amounts as whole rupees (Rs. 5,00,000 -> 500000).
- For each waiting period, record what the wording says it is counted from. Use "first_policy_date" only
  if the wording says so (or says continuous cover from the first policy counts), "policy_start" only if it
  says the current policy's start, otherwise "unclear". Include the clause number.
- The policy schedule is the source for numbers and dates; the wording is the source for rules."""


def _rupees(s: str) -> int | None:
    digits = re.sub(r"[^\d]", "", s)
    return int(digits) if digits else None


def _line_value(text: str, label: str) -> str | None:
    """Value after a label on the same line: 'Sum Insured Rs. 5,00,000' -> 'Rs. 5,00,000'."""
    m = re.search(rf"^\s*{label}\s*[:\-]?\s*(.+?)\s*$", text, re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else None


_INSURER = re.compile(r"^[A-Z][\w&.' ]{1,60}?\b(?:Insurance|Assurance)(?: Company)?(?: Limited| Ltd\.?)?$")


def _find_insurer(text: str) -> str | None:
    """The insurer's name from a line or line segment like 'Plan name - Navjeevan General Insurance
    Company Limited'. The longest match wins, so the full legal name beats a short header."""
    found = []
    for line in text.split("\n")[:80]:
        for part in re.split(r"\s+[-–|]\s+|,", line):
            part = part.strip()
            if _INSURER.match(part):
                found.append(part)
    return max(found, key=len) if found else None


_DOC_TITLE = r"(policy\s+)?(wording|schedule|terms\b.*|document|certificate)"


def _find_plan_name(text: str) -> str | None:
    """The plan name from the title block: 'DriveSure Comprehensive - Policy Wording' or, in a
    schedule, the line after 'Policy Schedule': 'Suraksha Health Plus - Navjeevan ... Limited'."""
    lines = [l.strip() for l in text.split("\n") if l.strip()][:4]
    for line in lines:
        line = re.sub(rf"\s*[-–|:]\s*{_DOC_TITLE}\s*$", "", line, flags=re.I)  # drop "- Policy Wording"
        parts = re.split(r"\s+[-–|]\s+", line)
        if len(parts) > 1 and _INSURER.match(parts[-1].strip()):  # drop "- <insurer>"
            line = " - ".join(parts[:-1])
        if re.fullmatch(_DOC_TITLE, line, re.I) or _INSURER.match(line) or re.match(r"\d", line):
            continue
        if re.match(r"(policy\s*(number|no|period)|sum\s*insured|policyholder|premium|uin)\b", line, re.I):
            continue  # a "Label value" field line, not a title
        if 2 < len(line) < 60:
            return line
    return None


def basic_terms(schedule_text: str, wording_text: str, clauses: list[SplitClause]) -> PolicyTerms:
    """Rule-based reading of the schedule and wording. Precise on well-formatted documents."""
    t = PolicyTerms()
    all_text = f"{schedule_text}\n{wording_text}"

    t.insurer = _find_insurer(all_text)
    t.policy_name = _find_plan_name(wording_text) or _find_plan_name(schedule_text)
    if re.search(r"hospitali[sz]ation|sum insured|in-patient", all_text, re.I):
        t.category = "health"
    elif re.search(r"own damage|vehicle|\bIDV\b|private car", all_text, re.I):
        t.category = "motor"

    if v := _line_value(schedule_text, r"policy\s*(?:number|no\.?)"):
        t.policy_number = v.split()[0]
    if v := _line_value(schedule_text, r"(?:policyholder|proposer|insured name)"):
        t.policyholder = v
    if v := _line_value(schedule_text, r"policy\s*period"):
        found = re.findall(DATE_PATTERN, v)
        if len(found) >= 2:
            t.policy_start, t.policy_end = iso(parse_date(found[0])), iso(parse_date(found[1]))
    if v := _line_value(all_text, r"first\s*policy\s*date"):
        if found := re.findall(DATE_PATTERN, v):
            t.first_policy_date = iso(parse_date(found[0]))
    if v := _line_value(schedule_text, r"(?:sum\s*insured|IDV|insured declared value)"):
        t.sum_insured = _rupees(v.split("(")[0])
    if v := _line_value(schedule_text, r"(?:total\s*)?premium"):
        amounts = re.findall(r"(?:Rs\.?|₹|INR)\s*([\d,]+)", v)
        if amounts:
            t.premium = _rupees(amounts[-1])
    t.room_rent_limit = _line_value(schedule_text, r"room\s*rent(?:\s*limit)?")
    t.icu_limit = _line_value(schedule_text, r"ICU(?:\s*limit)?")
    t.copayment = _line_value(schedule_text, r"co-?payment")

    for m in re.finditer(rf"([A-Z]{{2,}}/[\w/]+)\s+({DATE_PATTERN})\s*[-–to]+\s*({DATE_PATTERN})", schedule_text):
        t.policy_history.append(PolicyPeriod(policy_number=m.group(1), start=iso(parse_date(m.group(2))), end=iso(parse_date(m.group(3)))))
    t.policy_history.sort(key=lambda p: p.start or "")

    for c in clauses:
        body = f"{c.title}\n{c.text}"
        if not re.search(r"waiting|after \d+ months|\d+ months of continuous", body, re.I):
            continue
        m = re.search(r"(\d{1,2})\s*months", body, re.I)
        days = re.search(r"first\s+(\d{1,3})\s+days", body, re.I)
        months = int(m.group(1)) if m else (max(1, round(int(days.group(1)) / 30)) if days else None)
        if not months:
            continue
        lowered = body.lower()
        if "first policy date" in lowered or "first policy" in lowered:
            counted: CountedFrom = "first_policy_date"
        elif re.search(r"(start|commencement|inception) of (the )?(current )?policy", lowered):
            counted = "policy_start"
        else:
            counted = "unclear"
        t.waiting_periods.append(WaitingPeriod(name=c.title, months=months, applies_to=c.title, counted_from=counted, clause_ref=c.ref))
    return t


def _merge(primary: PolicyTerms, backup: PolicyTerms) -> PolicyTerms:
    """Fill empty fields of `primary` from `backup`; drop dates that don't parse."""
    merged = primary.model_copy()
    for name in PolicyTerms.model_fields:
        if getattr(merged, name) in (None, [], ""):
            setattr(merged, name, getattr(backup, name))
    for name in ("policy_start", "policy_end", "first_policy_date"):
        value = getattr(merged, name)
        if value and not parse_date(value):
            setattr(merged, name, getattr(backup, name))
    return merged


# When a provider limits prompt size, these clauses are sent first: they hold the key terms.
_TERM_PRIORITY = (r"waiting", r"co-?pay|room|limit|sum insured|deductible|depreciation", r"first policy|continuous|grace",
                  r"not covered|exclusion", r"add-?on", r"cover")


def condensed_wording(clauses: list[SplitClause], budget: int) -> str:
    """The clauses that matter most for key terms, in document order, within `budget` characters."""
    def rank(c: SplitClause) -> int:
        head = f"{c.section_title} {c.title}"
        return next((i for i, p in enumerate(_TERM_PRIORITY) if re.search(p, head, re.I)), len(_TERM_PRIORITY))

    chosen, used = set(), 0
    for c in sorted(clauses, key=lambda c: (rank(c), c.order)):
        block = len(c.ref) + len(c.title) + len(c.text) + 4
        if used + block > budget:
            continue
        chosen.add(c.order)
        used += block
    return "\n\n".join(f"{c.ref} {c.title}\n{c.text}" for c in clauses if c.order in chosen)


def extract_terms(
    schedule_text: str, wording_text: str, clauses: list[SplitClause], ai: AIClientProtocol | None
) -> tuple[PolicyTerms, str]:
    """Returns (terms, mode) where mode is "ai" or "basic"."""
    basic = basic_terms(schedule_text, wording_text, clauses)
    if ai is None:
        return basic, "basic"
    budget = ai.prompt_budget_chars
    if budget and len(schedule_text) + len(wording_text) > budget:
        schedule_text = schedule_text[: budget // 3]
        wording_text = condensed_wording(clauses, budget - len(schedule_text)) if clauses else wording_text[: budget - len(schedule_text)]
    prompt = (
        "<policy_schedule>\n" + (schedule_text or "(not provided)") + "\n</policy_schedule>\n\n"
        "<policy_wording>\n" + (wording_text or "(not provided)") + "\n</policy_wording>\n\n"
        "Extract the key terms of this policy."
    )
    try:
        terms = ai.extract(PolicyTerms, system=TERMS_SYSTEM, prompt=prompt, effort="medium")
    except AIError as e:
        log.warning("AI term extraction failed (%s); using basic mode", e)
        return basic, "basic"
    return _merge(terms, basic), "ai"
