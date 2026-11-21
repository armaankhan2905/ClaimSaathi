"""Rejection Check: read the insurer's letter, test each reason against the policy, build the evidence.

Reasons about waiting periods are decided by the rules engine with exact dates (the demo case:
the insurer counted from the latest renewal, the wording counts from the First Policy Date).
Other reasons get an AI reading of the cited clause, or "ask the insurer" without AI.
Every finding keeps structured data (codes, dates, clause numbers) so the screen can show it in
any language and the PDF report can be written in English.
"""

import logging
import re
from typing import Literal

from pydantic import BaseModel, Field

from ..ai import AIClientProtocol, AIError
from ..rules.coverage import add_months, continuous_cover, covered_on, waiting_status
from .ask import LANG_NAMES, ClauseView, best_sentence, find_clauses
from .dates import DATE_PATTERN, iso, parse_date
from .terms import PolicyPeriod, PolicyTerms

log = logging.getLogger(__name__)

ReasonType = Literal["waiting_period", "pre_existing", "exclusion", "documents", "late_intimation", "not_covered", "other"]
Status = Literal["contradicted", "supported", "unclear"]


# --------------------------------------------------------------------------- 1. what the letter says


class InsurerReason(BaseModel):
    type: ReasonType = Field(description="waiting_period | pre_existing | exclusion | documents | late_intimation | not_covered | other")
    text: str = Field(description="The insurer's reason, close to their own words (English)")
    clause_ref: str | None = Field(default=None, description="Clause number the insurer cites, e.g. '4.2'")
    insurer_counted_from: str | None = Field(default=None, description="For waiting periods: the date the insurer counted from, YYYY-MM-DD, if the letter says it")


class LetterFacts(BaseModel):
    claim_number: str | None = None
    policy_number: str | None = None
    patient: str | None = None
    hospital: str | None = None
    treatment: str | None = Field(default=None, description="Treatment or diagnosis, e.g. 'left total knee replacement'")
    admission_date: str | None = Field(default=None, description="YYYY-MM-DD")
    letter_date: str | None = Field(default=None, description="YYYY-MM-DD")
    claimed_amount: int | None = Field(default=None, description="Rupees")
    reasons: list[InsurerReason] = Field(default_factory=list)


LETTER_SYSTEM = """You read an Indian insurance claim rejection (repudiation) letter and record exactly what it says.
Dates as YYYY-MM-DD, amounts as whole rupees (Rs. 1,80,000 -> 180000). List every separate reason the insurer
gives for rejecting the claim, with the clause it cites and, for a waiting period, the date the insurer says it
counted from (e.g. "the policy commenced on 12 Mar 2026"). Leave fields null when the letter doesn't say."""


def _after(label: str, text: str) -> str | None:
    m = re.search(rf"{label}\s*[:\-]?\s*(.+)", text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def _reason_type(text: str) -> str:
    t = text.lower()
    if "pre-existing" in t or "pre existing" in t or "preexisting" in t:
        return "pre_existing"
    if "waiting period" in t:
        return "waiting_period"
    if re.search(r"intimat|informed late|delay in (?:informing|intimation)", t):
        return "late_intimation"
    if re.search(r"document|papers? (?:not|were not) (?:submitted|received)", t):
        return "documents"
    if re.search(r"exclu|excluded|not covered|not payable under", t):
        return "exclusion"
    return "other"


def basic_letter_facts(text: str) -> LetterFacts:
    f = LetterFacts()
    if m := re.search(r"\b([A-Z]{2,5}[-/]\d{2}[-/]\d{3,8})\b", text):
        f.claim_number = m.group(1)
    if v := _after(r"policy\s*(?:number|no\.?)", text):
        f.policy_number = v.split()[0]
    f.patient = _after(r"patient(?:\s*name)?", text)
    f.hospital = _after(r"hospital(?:\s*name)?", text)
    if v := _after(r"date\s*of\s*admission", text):
        if d := re.findall(DATE_PATTERN, v):
            f.admission_date = iso(parse_date(d[0]))
    if m := re.search(rf"(?im)^\s*date\s*[:\-]\s*({DATE_PATTERN})", text):  # the letter's own "Date:" line
        f.letter_date = iso(parse_date(m.group(1)))
    if v := _after(r"(?:claimed|claim)\s*amount", text):
        digits = re.sub(r"[^\d]", "", v.split("(")[0])
        f.claimed_amount = int(digits) if digits else None
    if m := re.search(r"claim for (.+?)(?: surgery)?\. ", text.replace("\n", " "), re.IGNORECASE):
        f.treatment = m.group(1).strip()[:120]
    reason = _after(r"reason", text)
    if reason:
        # The reason often runs over several lines: take the paragraph.
        start = text.lower().find("reason")
        para = text[start:].split("\n\n")[0].replace("\n", " ")
        para = re.sub(r"^reason\s*[:\-]?\s*", "", para, flags=re.IGNORECASE).strip()
        # OCR can lose the blank line before the sign-off: stop at the closing sentences.
        para = re.split(r"\s+(?:If you are not satisfied|You may (?:write|approach|contact)|Yours (?:faithfully|sincerely)|Regards)\b", para, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        ref = re.search(r"clause\s+(\d+(?:\.\d+)*)", para, re.IGNORECASE)
        started = re.search(rf"(?:commenced|started|began|inception)\s+on\s+({DATE_PATTERN})", para, re.IGNORECASE)
        f.reasons.append(
            InsurerReason(
                type=_reason_type(para),
                text=para[:600],
                clause_ref=ref.group(1) if ref else None,
                insurer_counted_from=iso(parse_date(started.group(1))) if started else None,
            )
        )
    return f


def read_letter(text: str, ai: AIClientProtocol | None) -> tuple[LetterFacts, str]:
    basic = basic_letter_facts(text)
    if ai is None:
        return basic, "basic"
    try:
        facts = ai.extract(LetterFacts, system=LETTER_SYSTEM, prompt=f"<letter>\n{text[:12000]}\n</letter>", max_tokens=1500, effort="medium")
    except AIError as e:
        log.warning("AI letter reading failed (%s); using rules", e)
        return basic, "basic"
    for name in LetterFacts.model_fields:  # fill gaps from the rules
        if getattr(facts, name) in (None, [], ""):
            setattr(facts, name, getattr(basic, name))
    for name in ("admission_date", "letter_date"):
        if getattr(facts, name) and not parse_date(getattr(facts, name)):
            setattr(facts, name, getattr(basic, name))
    return facts, "ai"


# --------------------------------------------------------------------------- 2. evidence from other documents


def periods_from_receipts(texts: list[str]) -> list[PolicyPeriod]:
    """Policy periods mentioned in renewal receipts or older schedules: 'NGI/HL/2024/310962 12 Mar 2024 - 11 Mar 2025'."""
    found = []
    for text in texts:
        for m in re.finditer(rf"(?:([A-Z]{{2,}}/[\w/]+)\s+)?(?:period\s*[:\-]?\s*)?({DATE_PATTERN})\s*(?:-|–|to)\s*({DATE_PATTERN})", text, re.IGNORECASE):
            start, end = parse_date(m.group(2)), parse_date(m.group(3))
            if start and end and 300 <= (end - start).days <= 400:  # a yearly policy period, not two random dates
                found.append(PolicyPeriod(policy_number=m.group(1), start=iso(start), end=iso(end)))
    return found


def merged_terms(terms: dict | None, extra_periods: list[PolicyPeriod]) -> PolicyTerms:
    t = PolicyTerms.model_validate(terms or {})
    have = {(p.start, p.end) for p in t.policy_history}
    for p in extra_periods:
        if (p.start, p.end) not in have:
            t.policy_history.append(p)
            have.add((p.start, p.end))
    t.policy_history.sort(key=lambda p: p.start or "")
    return t


# --------------------------------------------------------------------------- 3. checking each reason


class ReasonVerdict(BaseModel):
    status: Status = Field(description="contradicted (the policy doesn't support the insurer's reason) | supported (the policy supports it) | unclear (more information needed)")
    policy_says_en: str = Field(description="1-2 sentences in English: what the cited clause actually says about this")
    explanation_en: str = Field(description="1-3 sentences in English: whether the reason holds, and why")
    explanation_local: str = Field(description="The same explanation in the requested language")
    question_en: str = Field(description="One question the policyholder should ask the insurer about this reason, in English")
    question_local: str = Field(description="The same question in the requested language")
    evidence_needed: list[str] = Field(description="Documents that would help, in English, e.g. 'discharge summary showing first diagnosis date'")


VERDICT_SYSTEM = """You help an Indian policyholder check ONE reason an insurer gave for rejecting their claim, using only
the policy clauses and facts provided. Rules:
- "contradicted" only if the clauses clearly don't support the insurer's reason; "supported" only if they clearly
  do; otherwise "unclear". Never stretch a clause to mean something it doesn't say.
- Quote numbers, dates and clause numbers exactly. Write rupees the Indian way (Rs. 1,80,000).
- Be factual and calm: no legal advice, no promises that the claim will be paid.
- Write the _en fields in English and the _local fields in the requested language."""


def human_date(iso_date: str | None) -> str:
    """2022-03-12 -> 12 Mar 2022 (for English text sent to insurers)."""
    d = parse_date(iso_date)
    return d.strftime("%d %b %Y").lstrip("0") if d else (iso_date or "?")


def _clause_by_ref(clauses: list[ClauseView], ref: str | None) -> ClauseView | None:
    if not ref:
        return None
    ref = ref.strip().lstrip("§").rstrip(".")
    return next((c for c in clauses if c.ref == ref), None)


def _quote(c: ClauseView | None, hint: str) -> dict | None:
    return {"ref": c.ref, "title": c.title, "quote": best_sentence(c.text, hint)} if c else None


def _counting_quote(c: ClauseView | None, treatment: str | None) -> dict | None:
    """For a waiting period the key sentence is the one saying what it is counted from."""
    if c is None:
        return None
    for sentence in re.split(r"(?<=[.;])\s+", " ".join(c.text.split())):
        if re.search(r"counted from|count(?:ed|ing)? (?:the|from)", sentence, re.IGNORECASE):
            return {"ref": c.ref, "title": c.title, "quote": sentence.strip()}
    return _quote(c, f"{treatment or ''} months first policy date")


def check_waiting_reason(reason: InsurerReason, facts: LetterFacts, terms: PolicyTerms, clauses: list[ClauseView]) -> dict:
    """Decided by exact dates: when did the waiting period really end, compared with the admission date?"""
    admission = parse_date(facts.admission_date)
    wp = next((w for w in terms.waiting_periods if reason.clause_ref and w.clause_ref == reason.clause_ref.strip()), None)
    if wp is None and facts.treatment:  # the insurer didn't cite a clause: match the treatment to a waiting period
        treatment = facts.treatment.lower()
        for w in terms.waiting_periods:
            c = _clause_by_ref(clauses, w.clause_ref)
            words = [x for x in re.findall(r"[a-z]{4,}", treatment) if x not in ("left", "right", "total", "surgery")]
            if c and any(x in c.text.lower() for x in words):
                wp = w
                break
    clause = _clause_by_ref(clauses, (wp.clause_ref if wp else None) or reason.clause_ref)
    row = {
        "type": "waiting_period",
        "insurer_reason": reason.text,
        "clause_ref": clause.ref if clause else reason.clause_ref,
        "policy_quote": _counting_quote(clause, facts.treatment),
        "status": "unclear",
        "code": None,
        "data": {},
        "explanation_en": "",
        "explanation_local": "",
        "question_en": "",
        "question_local": "",
        "evidence": [],
    }
    if wp is None or admission is None:
        row["code"] = "waiting_unknown"
        row["question_en"] = "Please tell me which waiting period you applied, the clause it comes from, and the date you counted it from."
        return row

    status_ws = waiting_status(wp, terms, today=admission)
    cover = continuous_cover(terms)
    over = covered_on(status_ws, admission)
    insurer_from = parse_date(reason.insurer_counted_from)
    insurer_end = None
    if insurer_from:
        insurer_end = add_months(insurer_from, wp.months).isoformat()
    row["data"] = {
        "months": wp.months,
        "counted_from": wp.counted_from,
        "policy_start_for_waiting": status_ws.starts,
        "waiting_ends": status_ws.ends,
        "admission_date": facts.admission_date,
        "insurer_counted_from": reason.insurer_counted_from,
        "insurer_waiting_ends": insurer_end,
        "continuous_since": cover.continuous_since,
        "periods_checked": cover.periods_checked,
        "breaks": [b.__dict__ for b in cover.breaks],
    }
    row["evidence"] = ["policy_history"] if cover.periods_checked >= 2 else []
    if over is True:
        row["status"] = "contradicted"
        mismatch = insurer_from is not None and status_ws.starts is not None and reason.insurer_counted_from != status_ws.starts
        row["code"] = "waiting_over_counted_wrongly" if mismatch else "waiting_over"
        row["question_en"] = (
            f"Clause {row['clause_ref']} counts the {wp.months}-month waiting period from the First Policy Date "
            f"({human_date(status_ws.starts)}) with continuous cover, so it ended on {human_date(status_ws.ends)}, "
            f"before my admission on {human_date(facts.admission_date)}. "
            + (f"Why was it counted from {human_date(reason.insurer_counted_from)} instead? " if mismatch else "")
            + "Please review the claim on this basis."
        )
    elif over is False:
        row["status"] = "supported"
        row["code"] = "waiting_not_over_break" if cover.breaks else "waiting_not_over"
        row["question_en"] = (
            f"Please confirm the start date you used for the {wp.months}-month waiting period and whether any earlier "
            "continuous cover (including portability) was credited."
        )
    else:
        row["code"] = "waiting_unknown"
        row["question_en"] = "Please tell me the date you counted the waiting period from."
    if wp.counted_from == "unclear":
        row["status"] = "unclear"
        row["code"] = "waiting_basis_unclear"
    return row


def check_other_reason(reason: InsurerReason, facts: LetterFacts, terms: PolicyTerms, clauses: list[ClauseView], lang: str, ai: AIClientProtocol | None) -> dict:
    clause = _clause_by_ref(clauses, reason.clause_ref)
    related = [clause] if clause else []
    for c in find_clauses(f"{reason.text} {facts.treatment or ''}", clauses, 3):
        if c not in related:
            related.append(c)
    row = {
        "type": reason.type,
        "insurer_reason": reason.text,
        "clause_ref": clause.ref if clause else reason.clause_ref,
        "policy_quote": _quote(clause or (related[0] if related else None), reason.text),
        "status": "unclear",
        "code": f"{reason.type}_check",
        "data": {},
        "explanation_en": "",
        "explanation_local": "",
        "question_en": {
            "pre_existing": "Please share the medical record you relied on to treat this as a pre-existing disease, and the date of first diagnosis it shows.",
            "documents": "Please list exactly which documents are missing so I can send them.",
            "late_intimation": "Please confirm the date you say the claim was intimated and the clause that sets the time limit.",
        }.get(reason.type, "Please explain how the clause you cited applies to my treatment."),
        "question_local": "",
        "evidence": [],
    }
    if reason.clause_ref and clause is None:
        row["code"] = "clause_not_found"
    if ai is None or not related:
        return row

    blocks = "\n\n".join(f'<clause ref="{c.ref}" title="{c.title}">\n{c.text}\n</clause>' for c in related)
    facts_txt = f"Treatment: {facts.treatment}\nAdmission: {facts.admission_date}\nContinuous cover since: {continuous_cover(terms).continuous_since}"
    prompt = (
        f"<facts>\n{facts_txt}\n</facts>\n\n{blocks}\n\n<insurer_reason clause=\"{reason.clause_ref or ''}\">{reason.text}</insurer_reason>\n"
        f"Write the _local fields in {LANG_NAMES.get(lang, LANG_NAMES['en'])}."
    )
    try:
        v = ai.extract(ReasonVerdict, system=VERDICT_SYSTEM, prompt=prompt, max_tokens=1200, effort="medium")
    except AIError as e:
        log.warning("AI reason check failed (%s)", e)
        return row
    row.update(
        status=v.status,
        code=f"{reason.type}_ai",
        explanation_en=v.explanation_en.strip(),
        explanation_local=v.explanation_local.strip(),
        question_en=v.question_en.strip() or row["question_en"],
        question_local=v.question_local.strip(),
        evidence=[e for e in v.evidence_needed if e.strip()][:4],
    )
    row["data"]["policy_says_en"] = v.policy_says_en.strip()
    return row


# --------------------------------------------------------------------------- 4. putting it together


def build_timeline(facts: LetterFacts, terms: PolicyTerms, rows: list[dict]) -> list[dict]:
    """Dated events, oldest first: {"date", "kind", ...} with kinds the UI translates."""
    events: list[dict] = []
    cover = continuous_cover(terms)
    if cover.continuous_since:
        events.append({"date": cover.continuous_since, "kind": "first_policy"})
    for p in terms.policy_history[1:]:
        if p.start:
            events.append({"date": p.start, "kind": "renewal"})
    for b in cover.breaks:
        events.append({"date": b.previous_end, "kind": "break", "until": b.next_start, "days": b.gap_days})
    for r in rows:
        d = r.get("data") or {}
        if r["type"] == "waiting_period" and d.get("waiting_ends"):
            events.append({"date": d["waiting_ends"], "kind": "waiting_ends", "months": d["months"], "clause_ref": r["clause_ref"]})
        if r["type"] == "waiting_period" and d.get("insurer_counted_from"):
            events.append({"date": d["insurer_counted_from"], "kind": "insurer_start"})
    if facts.admission_date:
        events.append({"date": facts.admission_date, "kind": "admission"})
    if facts.letter_date:
        events.append({"date": facts.letter_date, "kind": "rejection"})
    order = {"first_policy": 0, "renewal": 1, "insurer_start": 2, "break": 3, "waiting_ends": 4, "admission": 5, "rejection": 6}
    seen, unique = set(), []
    for e in sorted(events, key=lambda e: (e["date"], order.get(e["kind"], 9))):
        key = (e["date"], e["kind"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


def build_checklist(kinds_present: set[str], terms: PolicyTerms, policy_has_wording: bool, rows: list[dict]) -> list[dict]:
    needs_history = any(r["type"] == "waiting_period" for r in rows)
    items = [
        ("rejection_letter", "rejection_letter" in kinds_present, True),
        ("policy_wording", policy_has_wording, True),
        ("policy_history", len(terms.policy_history) >= 2 or "renewal_receipt" in kinds_present, needs_history),
        ("discharge_summary", "discharge_summary" in kinds_present, True),
        ("hospital_bill", "hospital_bill" in kinds_present, True),
        ("doctor_note", "doctor_note" in kinds_present, any(r["type"] == "pre_existing" for r in rows)),
    ]
    return [{"item": key, "have": have, "important": important} for key, have, important in items]


def assess(rows: list[dict]) -> str:
    if any(r["status"] == "contradicted" for r in rows):
        return "inconsistency"
    if rows and all(r["status"] == "supported" for r in rows):
        return "consistent"
    return "needs_info"


def check_claim(
    letter_text: str,
    other_texts: dict[str, list[str]],
    terms: dict | None,
    clauses: list[ClauseView],
    policy_has_wording: bool,
    lang: str,
    ai: AIClientProtocol | None,
) -> tuple[dict, dict, str]:
    """Returns (facts, findings, mode). `other_texts` maps document kind -> texts of the claim's other documents."""
    facts, letter_mode = read_letter(letter_text, ai)
    extra = periods_from_receipts(other_texts.get("renewal_receipt", []) + other_texts.get("previous_policy", []))
    t = merged_terms(terms, extra)

    rows = []
    for reason in facts.reasons or [InsurerReason(type="other", text="(The letter gives no clear reason.)")]:
        if reason.type == "waiting_period":
            rows.append(check_waiting_reason(reason, facts, t, clauses))
        else:
            rows.append(check_other_reason(reason, facts, t, clauses, lang, ai))

    findings = {
        "assessment": assess(rows),
        "rows": rows,
        "timeline": build_timeline(facts, t, rows),
        "checklist": build_checklist(set(other_texts) | {"rejection_letter"}, t, policy_has_wording, rows),
        "questions": [{"en": r["question_en"], "local": r.get("question_local") or ""} for r in rows if r.get("question_en")],
        "policy": {"continuous_since": continuous_cover(t).continuous_since, "periods": len(t.policy_history)},
    }
    mode = "ai" if ai is not None and (letter_mode == "ai" or any(r["code"].endswith("_ai") for r in rows if r["code"])) else "basic"
    return facts.model_dump(), findings, mode

