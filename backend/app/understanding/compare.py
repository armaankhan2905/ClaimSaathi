"""Compare two policies: by real situations, and feature by feature.

A situation ("knee replacement in year 3") is tested against each policy's own clauses. The
"year" is turned into a month of holding the policy, so waiting periods are checked with exact
numbers instead of each policy's real start date: we compare the products, as if both were
bought on the same day.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field

from ..ai import AIClientProtocol, AIError
from .ask import LANG_NAMES, ClauseView, _norm, best_sentence, find_clauses
from .terms import PolicyTerms

log = logging.getLogger(__name__)

Verdict = Literal["covered", "partly_covered", "not_covered", "unclear"]
VERDICT_RANK = {"covered": 3, "partly_covered": 2, "unclear": 1, "not_covered": 0}


@dataclass(frozen=True)
class Scenario:
    key: str
    category: str  # health | motor
    text: str  # English description used for search and for the AI
    month: int | None  # month of holding the policy when it happens (None = timing doesn't matter)
    keywords: tuple[str, ...]  # for basic mode


SCENARIOS: list[Scenario] = [
    Scenario("knee_year3", "health", "Knee replacement surgery in the 3rd year of the policy (month 30)", 30, ("knee", "joint replacement")),
    Scenario("private_room", "health", "A 5-day hospital stay in a single private room costing Rs. 8,000 per day", None, ("room", "private room", "room rent")),
    Scenario("maternity_year2", "health", "Childbirth (delivery) in the 2nd year of the policy (month 18)", 18, ("maternity", "childbirth", "delivery")),
    Scenario("diabetes_year3", "health", "Hospitalisation for diabetes that existed before buying the policy, in the 3rd year (month 30)", 30, ("pre-existing", "diabetes")),
    Scenario("cataract_year4", "health", "Cataract surgery on one eye costing Rs. 60,000 in the 4th year of the policy (month 42)", 42, ("cataract",)),
    Scenario("accident_ambulance", "health", "A road accident in the first year needing an ambulance and 3 days in hospital (month 6)", 6, ("ambulance", "accident")),
    Scenario("abroad", "health", "Treatment taken outside India", None, ("outside india", "abroad")),
    Scenario("flood_engine", "motor", "Engine damage after driving through a flooded road", None, ("engine", "water", "flood")),
    Scenario("bumper_zero_dep", "motor", "Replacing a damaged plastic bumper after a minor accident", None, ("depreciation", "plastic", "bumper")),
    Scenario("no_licence", "motor", "An accident while the car was driven by someone without a valid licence", None, ("licence", "license")),
]
SCENARIO_BY_KEY = {s.key: s for s in SCENARIOS}


class PolicyVerdict(BaseModel):
    verdict: Verdict = Field(description="covered | partly_covered (paid with a limit, sub-limit, co-pay or deduction) | not_covered | unclear")
    summary: str = Field(description="1-3 short sentences in the requested language: what this policy would do in this situation and why")
    what_you_pay: str = Field(description="Short note in the requested language on limits, co-pay or deductions that apply; empty if none")
    citations: list["ScenarioCitation"] = Field(description="Clauses relied on, most important first")


class ScenarioCitation(BaseModel):
    ref: str
    quote: str = Field(description="A short exact quote (under 25 words) copied from that clause")


PolicyVerdict.model_rebuild()

VERDICT_SYSTEM = """You test a real-life situation against ONE Indian health or motor insurance policy, using only
its clauses and the facts given. Rules:
- Decide covered / partly_covered / not_covered / unclear from the clauses. partly_covered means it is paid but
  a limit, sub-limit, co-payment or deduction reduces the amount.
- Assume the policy was bought new and the situation happens in the month of holding the policy given in the
  facts; compare that month with each waiting period's length.
- If no clause addresses the situation, say "unclear" and that the policy doesn't mention it. Never stretch a
  clause to mean something it doesn't say.
- Keep amounts and clause numbers exactly as in the policy; write rupees the Indian way (Rs. 5,00,000).
- Cite the clauses you rely on with a short quote copied word for word.
- Write the summary and what_you_pay in the requested language."""


@dataclass
class PolicyResult:
    verdict: str
    summary: str
    what_you_pay: str = ""
    citations: list[dict] = field(default_factory=list)  # {"ref", "title", "quote"}
    mode: str = "basic"
    # basic mode only, translated by the UI: {"code": "waiting_not_over", "months": 36} | {"code": "excluded"}
    # | {"code": "limited"} | {"code": "mentioned"} | {"code": "not_mentioned"}
    reason: dict | None = None


def _facts(terms: dict | None, month: int | None) -> str:
    t = PolicyTerms.model_validate(terms or {})
    lines = [f"The situation happens in month {month} of holding the policy." if month else "The timing doesn't matter for this situation."]
    for w in t.waiting_periods:
        state = "" if month is None else (" (already over by then)" if month >= w.months else " (NOT over by then)")
        lines.append(f"Waiting period '{w.name}' (clause {w.clause_ref}): {w.months} months{state}")
    for label, value in (("Sum insured", f"Rs. {t.sum_insured:,}" if t.sum_insured else None), ("Room rent limit", t.room_rent_limit), ("Co-payment", t.copayment)):
        if value:
            lines.append(f"{label}: {value}")
    return "\n".join(lines)


def _basic_verdict(scenario_text: str, keywords: tuple[str, ...], month: int | None, clauses: list[ClauseView], terms: dict | None) -> PolicyResult:
    """Rule-based: a waiting period not yet over, or an exclusion mentioning the situation, means not
    covered; a matching limit means partly; a matching coverage clause means covered."""
    t = PolicyTerms.model_validate(terms or {})
    kws = [k.lower() for k in keywords] or re.findall(r"[a-z]{4,}", scenario_text.lower())

    def mentions(c: ClauseView) -> bool:
        body = f"{c.title} {c.text}".lower()
        return any(k in body for k in kws)

    def cite(c: ClauseView) -> dict:
        return {"ref": c.ref, "title": c.title, "quote": best_sentence(c.text, " ".join(kws))}

    by_ref = {c.ref: c for c in clauses}
    if month is not None:
        for w in t.waiting_periods:
            c = by_ref.get(w.clause_ref or "")
            if c and mentions(c) and month < w.months:
                return PolicyResult("not_covered", "", citations=[cite(c)], reason={"code": "waiting_not_over", "months": w.months})
    for category, verdict, code in (("exclusion", "not_covered", "excluded"), ("limit", "partly_covered", "limited"), ("coverage", "covered", "mentioned")):
        hits = [c for c in clauses if c.category == category and mentions(c)]
        if hits:
            return PolicyResult(verdict, "", citations=[cite(c) for c in hits[:2]], reason={"code": code})
    if month is not None:  # a waiting period for it exists and is over by then
        for w in t.waiting_periods:
            c = by_ref.get(w.clause_ref or "")
            if c and mentions(c):
                return PolicyResult("covered", "", citations=[cite(c)], reason={"code": "waiting_over", "months": w.months})
    return PolicyResult("unclear", "", citations=[cite(c) for c in find_clauses(scenario_text, clauses, 2)], reason={"code": "not_mentioned"})


def evaluate(
    scenario_text: str,
    keywords: tuple[str, ...],
    month: int | None,
    lang: str,
    clauses: list[ClauseView],
    terms: dict | None,
    ai: AIClientProtocol | None,
) -> PolicyResult:
    if ai is None:
        return _basic_verdict(scenario_text, keywords, month, clauses, terms)
    found = find_clauses(scenario_text, clauses, 5)
    # The waiting-period and exclusion clauses decide most situations: make sure they're in view.
    for c in clauses:
        if c.category in ("waiting_period", "exclusion") and c not in found and len(found) < 8:
            found.append(c)
    blocks = "\n\n".join(f'<clause ref="{c.ref}" title="{c.title}">\n{c.text}\n</clause>' for c in found)
    prompt = f"<facts>\n{_facts(terms, month)}\n</facts>\n\n{blocks}\n\nAnswer in {LANG_NAMES.get(lang, LANG_NAMES['en'])}.\n<situation>{scenario_text}</situation>"
    if ai.prompt_budget_chars and len(prompt) > ai.prompt_budget_chars:
        prompt = prompt[: ai.prompt_budget_chars]
    try:
        r = ai.extract(PolicyVerdict, system=VERDICT_SYSTEM, prompt=prompt, max_tokens=1200, effort="medium")
    except AIError as e:
        log.warning("AI verdict failed (%s); using rules", e)
        return _basic_verdict(scenario_text, keywords, month, clauses, terms)

    by_ref = {c.ref: c for c in found}
    cites, seen = [], set()
    for cit in r.citations:
        c = by_ref.get(cit.ref.strip().lstrip("§"))
        if c is None or c.ref in seen:
            continue
        seen.add(c.ref)
        quote = cit.quote.strip().strip('"“”')
        if not quote or _norm(quote) not in _norm(c.text):
            quote = best_sentence(c.text, scenario_text)
        cites.append({"ref": c.ref, "title": c.title, "quote": quote})
    return PolicyResult(r.verdict, r.summary.strip(), r.what_you_pay.strip(), cites, "ai")


def month_from_text(text: str) -> int | None:
    """'in the 3rd year' -> 30 (middle of year 3), 'after 20 months' -> 20, 'year 2' -> 18."""
    if m := re.search(r"(\d{1,2})\s*(?:st|nd|rd|th)?\s*(?:year|saal|वर्ष|साल)", text, re.I) or re.search(r"(?:year|saal)\s*(\d{1,2})", text, re.I):
        return (int(m.group(1)) - 1) * 12 + 6
    if m := re.search(r"(\d{1,3})\s*(?:months?|mahine|महीने)", text, re.I):
        return int(m.group(1))
    return None


def winner(a: PolicyResult, b: PolicyResult) -> str:
    """"a", "b" or "tie" for this situation."""
    ra, rb = VERDICT_RANK.get(a.verdict, 1), VERDICT_RANK.get(b.verdict, 1)
    return "a" if ra > rb else "b" if rb > ra else "tie"


# --------------------------------------------------------------------------- feature table

_WAIT_ROWS = (
    ("wait_initial", r"initial"),
    ("wait_specified", r"specified|listed|specific|named"),
    ("wait_ped", r"pre-?existing"),
    ("wait_maternity", r"maternity"),
)


def _waiting(terms: PolicyTerms, pattern: str) -> int | None:
    for w in terms.waiting_periods:
        if re.search(pattern, f"{w.name} {w.applies_to}", re.I):
            return w.months
    return None


def _maternity(clauses: list[ClauseView]) -> str | None:
    for c in clauses:
        body = f"{c.title} {c.text}".lower()
        if "maternity" in body or "childbirth" in body:
            if c.category == "exclusion":
                return "not_covered"
            if c.category in ("coverage", "limit", "waiting_period") and "maternity" in c.title.lower():
                return "covered"
    return None


def _no_limit(text: str | None) -> bool:
    return bool(text) and bool(re.search(r"\bnone\b|no limit|any (single )?private|in full|no co-?pay", text, re.I))


def feature_table(terms_a: dict | None, terms_b: dict | None, clauses_a: list[ClauseView], clauses_b: list[ClauseView]) -> list[dict]:
    """Rows of {"key", "a", "b", "better"} with better = "a" | "b" | None. Values are numbers,
    short texts from the documents, or codes the UI translates ("covered", "not_covered")."""
    ta, tb = PolicyTerms.model_validate(terms_a or {}), PolicyTerms.model_validate(terms_b or {})
    rows: list[dict] = []

    def add(key, a, b, better=None):
        if a is not None or b is not None:
            rows.append({"key": key, "a": a, "b": b, "better": better})

    def higher(a, b):
        return None if a is None or b is None or a == b else ("a" if a > b else "b")

    def lower(a, b):
        return None if a is None or b is None or a == b else ("a" if a < b else "b")

    def freer(a, b):  # "no limit / none" beats a stated limit
        na, nb = _no_limit(a), _no_limit(b)
        return None if na == nb or a is None or b is None else ("a" if na else "b")

    add("sum_insured", ta.sum_insured, tb.sum_insured, higher(ta.sum_insured, tb.sum_insured))
    add("premium", ta.premium, tb.premium, lower(ta.premium, tb.premium))
    add("room_rent", ta.room_rent_limit, tb.room_rent_limit, freer(ta.room_rent_limit, tb.room_rent_limit))
    add("copay", ta.copayment, tb.copayment, freer(ta.copayment, tb.copayment))
    for key, pattern in _WAIT_ROWS:
        a, b = _waiting(ta, pattern), _waiting(tb, pattern)
        add(key, a, b, lower(a, b))
    ma, mb = _maternity(clauses_a), _maternity(clauses_b)
    add("maternity", ma, mb, None if ma == mb or None in (ma, mb) else ("a" if ma == "covered" else "b"))
    add("exclusions_count", len(ta.key_exclusions) or None, len(tb.key_exclusions) or None, None)
    return rows
