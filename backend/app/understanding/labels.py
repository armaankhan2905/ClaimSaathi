"""Categorise clauses and explain each one in plain English, Hindi and Hinglish."""

import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

from pydantic import BaseModel, Field

from ..ai import AIClientProtocol, AIError
from .clauses import SplitClause

log = logging.getLogger(__name__)

Category = Literal["coverage", "exclusion", "limit", "waiting_period", "definition", "condition", "claim_process", "grievance", "other"]


class ClauseLabel(BaseModel):
    ref: str
    category: Category
    plain_en: str = Field(description="1-3 short sentences in simple English")
    plain_hi: str = Field(description="The same explanation in simple Hindi (Devanagari script)")
    plain_hn: str = Field(description="The same explanation in Hinglish (Hindi in Roman script, everyday English words kept)")


class ClauseLabels(BaseModel):
    items: list[ClauseLabel]


LABEL_SYSTEM = """You explain Indian insurance policy clauses to ordinary policyholders.
For each clause give:
- category: coverage (what is paid for), exclusion (what is not), limit (caps, sub-limits, co-payment,
  deductions), waiting_period, definition, condition (duties, renewal, cancellation), claim_process,
  grievance, or other.
- A plain explanation in 1-3 short sentences: what it means for the policyholder in practice. Keep every
  number, amount and time period exactly as in the clause, attached to what it measures ("ICU up to 2% of
  the sum insured per day", never "2% of ICU charges"). Do not add rules, advice or opinions that are not
  in the clause. Write "you" for the policyholder and "the insurer" for the company.
- The same explanation in simple Hindi (Devanagari) and in Hinglish (Roman script, the way people text).
  These must say exactly what the English says, with the same numbers attached to the same things.
Return one item per clause, using the clause numbers given."""

# Rule-based categories for basic mode, checked against the section title, then the clause title.
_RULES: list[tuple[str, Category]] = [
    (r"waiting", "waiting_period"),
    (r"definition", "definition"),
    (r"not covered|exclusion", "exclusion"),
    (r"grievance|complaint|ombudsman", "grievance"),
    (r"claim", "claim_process"),
    (r"co-?pay|limit|sub-?limit|deductible|depreciation|room rent", "limit"),
    (r"renewal|cancell|free look|condition|portability|grace", "condition"),
    (r"covered|cover|benefit|expenses|treatment|own damage|liability|add-on", "coverage"),
]


# Sections whose name decides the category of everything in them ("Grace Period" under
# "Definitions" is a definition, not a renewal condition).
_STRONG_SECTIONS: set[Category] = {"definition", "waiting_period", "exclusion", "grievance", "claim_process"}


def _match(text: str) -> Category | None:
    for pattern, category in _RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return category
    return None


def basic_category(c: SplitClause) -> Category:
    if c.section_title != c.title and re.search(r"add-?ons?\b", c.section_title, re.IGNORECASE):
        return "coverage"  # "Zero Depreciation" under Add-ons is extra cover, not a limit
    section = _match(c.section_title) if c.section_title != c.title else None
    if section in _STRONG_SECTIONS:
        return section
    return _match(c.title) or section or "other"


def _label_batch(ai: AIClientProtocol, batch: list[SplitClause]) -> dict[str, ClauseLabel]:
    prompt = "\n\n".join(f"<clause ref=\"{c.ref}\" section=\"{c.section_title}\">\n{c.title}\n{c.text}\n</clause>" for c in batch)
    result = ai.extract(ClauseLabels, system=LABEL_SYSTEM, prompt=prompt, effort="low")
    return {item.ref: item for item in result.items}


def label_clauses(clauses: list[SplitClause], ai: AIClientProtocol | None) -> tuple[list[tuple[str, dict | None]], str]:
    """Returns ([(category, {"en","hi","hn"} or None) per clause], mode)."""
    basic = [(basic_category(c), None) for c in clauses]
    if ai is None or not clauses:
        return basic, "basic"

    size = ai.clause_batch_size  # sized per provider (Groq's free plan needs small requests)
    batches = [list(range(i, min(i + size, len(clauses)))) for i in range(0, len(clauses), size)]

    def run(idx: list[int]) -> dict[int, ClauseLabel]:
        # One retry, and a failed batch only costs its own clauses their explanations (a single
        # rate-limit error used to drop every explanation in the policy).
        batch = [clauses[i] for i in idx]
        for attempt in (1, 2):
            try:
                by_ref = _label_batch(ai, batch)
                return {i: by_ref[clauses[i].ref] for i in idx if clauses[i].ref in by_ref}
            except AIError as e:
                log.warning("AI clause labelling failed for %s (attempt %s): %s", [c.ref for c in batch], attempt, e)
        return {}

    labelled: dict[int, ClauseLabel] = {}
    with ThreadPoolExecutor(max_workers=ai.parallel_requests) as pool:
        for part in pool.map(run, batches):
            labelled.update(part)
    if not labelled:
        return basic, "basic"

    out = []
    for i, fallback in enumerate(basic):
        item = labelled.get(i)
        if item is None:  # the model skipped a clause or its batch failed: rule-based category, no explanation
            out.append(fallback)
        else:
            out.append((item.category, {"en": item.plain_en, "hi": item.plain_hi, "hn": item.plain_hn}))
    return out, "ai"
