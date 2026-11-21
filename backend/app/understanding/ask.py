"""Ask ClaimSaathi: answer a question about one policy, from its own clauses.

1. Find the clauses most relevant to the question (multilingual hybrid search).
2. Add facts the rules engine computed (continuous cover, waiting-period end dates), so
   "is my knee surgery covered now?" gets an answer with real dates.
3. Ask the AI to answer only from those clauses and facts, in the user's language, citing
   clause numbers with a short quote from each.
4. Check the citations: unknown clause numbers are dropped and quotes that are not word for
   word in the clause are replaced with real text from it.
Without AI it returns the most relevant clauses with their plain-language explanations.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from ..ai import AIClientProtocol, AIError
from ..rules.coverage import policy_timeline
from .search import SearchDoc, clause_search_text, from_bytes, search
from .terms import PolicyTerms

log = logging.getLogger(__name__)

TOP_K = 5
LANG_NAMES = {"en": "simple English", "hi": "simple Hindi in Devanagari script", "hn": "Hinglish (Hindi in Roman script, everyday English words kept)"}
AnswerType = Literal["answered", "not_in_policy", "needs_more_info"]


class Citation(BaseModel):
    ref: str = Field(description="Clause number exactly as given, e.g. '4.2'")
    quote: str = Field(description="A short exact quote (under 30 words) copied from that clause's text")


class AskAnswer(BaseModel):
    answer_type: AnswerType = Field(description="answered | not_in_policy (the clauses don't cover it) | needs_more_info")
    answer: str = Field(description="2-5 short sentences in the requested language")
    citations: list[Citation] = Field(description="The clauses the answer relies on, most important first")
    follow_ups: list[str] = Field(description="Up to 3 short follow-up questions the user might ask next, in the requested language")


ASK_SYSTEM = """You are ClaimSaathi, helping an Indian policyholder understand their own insurance policy.
Answer ONLY from the policy clauses and the computed facts provided. Rules:
- If no clause directly addresses the question, set answer_type to "not_in_policy" and say plainly that your
  policy documents don't mention it; never fill the gap with general insurance knowledge.
- Never stretch a clause to mean something it doesn't say. For example "a hospital outside the network" is
  not "treatment outside India", and "day care" is not "outpatient consultation".
- Say what the policy says ("this should be covered under clause 4.2") rather than promising the insurer
  "will pay"; the final decision is the insurer's.
- If the answer depends on something you don't know (e.g. whether the treatment was due to an accident), give
  the answer for each case and set answer_type to "needs_more_info".
- Use the computed facts for dates (waiting periods, continuous cover); they come from exact date checks.
- Keep numbers, amounts and clause numbers exactly as in the policy; write rupee amounts the Indian way
  (Rs. 5,00,000, not 500,000). Write "you" for the policyholder and
  "the insurer" for the company. No legal advice.
- Cite every clause you rely on with a short quote copied word for word from that clause.
- Write the answer and follow-ups in the requested language. Clause numbers stay as digits (e.g. 4.2)."""


@dataclass
class ClauseView:
    """What answering needs from a stored clause."""

    id: int
    ref: str
    title: str
    section_title: str
    text: str
    category: str
    plain: dict | None
    embedding: bytes | None


@dataclass
class AskResult:
    answer_type: str  # answered | not_in_policy | needs_more_info | search_only
    answer: str
    citations: list[dict] = field(default_factory=list)  # {"ref", "title", "quote", "clause_id"}
    follow_ups: list[str] = field(default_factory=list)
    mode: str = "basic"  # ai | basic


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def best_sentence(text: str, query: str, max_words: int = 40) -> str:
    """The sentence of a clause sharing the most words with the query (a fallback quote)."""
    sentences = [s.strip() for s in re.split(r"(?<=[.;:])\s+|\n+", text) if len(s.strip()) > 15]
    if not sentences:
        return " ".join(text.split()[:max_words])
    q = set(re.findall(r"\w{3,}", query.lower()))
    best = max(sentences, key=lambda s: len(q & set(re.findall(r"\w{3,}", s.lower()))))
    words = best.split()
    return " ".join(words[:max_words]) + ("…" if len(words) > max_words else "")


def retrieval_query(question: str, history: list[dict]) -> str:
    """Short follow-ups ("and for cataract?") are searched together with the previous question."""
    if len(question.split()) <= 5:
        previous = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
        if previous:
            return f"{previous} {question}"
    return question


def facts_text(terms: dict | None, today: date | None = None) -> str:
    if not terms:
        return "(no computed facts)"
    t = PolicyTerms.model_validate(terms)
    tl = policy_timeline(t, today)
    lines = []
    if t.policy_start or t.policy_end:
        lines.append(f"Current policy period: {t.policy_start or '?'} to {t.policy_end or '?'}")
    if tl["continuous_since"]:
        lines.append(f"Continuous cover with this insurer since: {tl['continuous_since']}")
    for b in tl["breaks"]:
        lines.append(f"Break in cover: {b['previous_end']} to {b['next_start']} ({b['gap_days']} days)")
    if t.sum_insured:
        lines.append(f"Sum insured: Rs. {t.sum_insured:,}")
    for w in tl["waiting_periods"]:
        state = "already over" if w["completed"] else f"not over yet ({w['days_left']} days left)" if w["completed"] is False else "unknown"
        lines.append(
            f"Waiting period '{w['name']}' (clause {w['clause_ref']}): {w['months']} months counted from {w['starts']}"
            f" ({w['counted_from']}), ends {w['ends']}: {state}"
        )
    lines.append(f"Today's date: {(today or date.today()).isoformat()}")
    return "\n".join(lines)


def find_clauses(question: str, clauses: list[ClauseView], k: int = TOP_K) -> list[ClauseView]:
    docs = [SearchDoc(i, c.ref, clause_search_text(c.ref, c.title, c.section_title, c.text), from_bytes(c.embedding) if c.embedding else None) for i, c in enumerate(clauses)]
    return [clauses[i] for i, _ in search(question, docs, k)]


def gather_clauses(question: str, history: list[dict], clauses: list[ClauseView], k: int = TOP_K) -> list[ClauseView]:
    """The question's own matches come first; matches for question + previous question only fill
    the remaining places. So a short new question ("मैटरनिटी का खर्च?") isn't drowned out by the
    previous topic, while a real follow-up ("and cataract?") still gets that topic's clauses."""
    own = find_clauses(question, clauses, k)
    combined_query = retrieval_query(question, history)
    if combined_query == question:
        return own
    picked = own[: max(3, k - 2)]
    for c in find_clauses(combined_query, clauses, k):
        if len(picked) >= k:
            break
        if c not in picked:
            picked.append(c)
    for c in own:  # still room: the rest of the question's own matches
        if len(picked) >= k:
            break
        if c not in picked:
            picked.append(c)
    return picked


def answer_question(
    question: str,
    lang: str,
    clauses: list[ClauseView],
    terms: dict | None,
    history: list[dict],
    ai: AIClientProtocol | None,
) -> AskResult:
    found = gather_clauses(question, history, clauses)
    if not found:
        return AskResult("not_in_policy", "", [], [], "ai" if ai else "basic")

    if ai is not None:
        try:
            return _ai_answer(question, lang, found, terms, history, ai)
        except AIError as e:
            log.warning("AI answer failed (%s); showing matching clauses instead", e)

    # Basic mode: the most relevant clauses with their explanations.
    return AskResult(
        answer_type="search_only",
        answer="",
        citations=[
            {"ref": c.ref, "title": c.title, "quote": (c.plain or {}).get(lang) or best_sentence(c.text, question), "clause_id": c.id}
            for c in found[:3]
        ],
        mode="basic",
    )


def _ai_answer(question: str, lang: str, found: list[ClauseView], terms: dict | None, history: list[dict], ai: AIClientProtocol) -> AskResult:
    budget = ai.prompt_budget_chars or 60_000
    clause_blocks, used = [], 0
    for c in found:
        block = f'<clause ref="{c.ref}" title="{c.title}" section="{c.section_title}">\n{c.text}\n</clause>'
        if used + len(block) > budget * 0.7:
            break
        clause_blocks.append(block)
        used += len(block)
    recent = "\n".join(f"{m['role']}: {m['content'][:400]}" for m in history[-4:])
    prompt = (
        f"<computed_facts>\n{facts_text(terms)}\n</computed_facts>\n\n"
        + "\n\n".join(clause_blocks)
        + (f"\n\n<earlier_conversation>\n{recent}\n</earlier_conversation>" if recent else "")
        + f"\n\nAnswer in {LANG_NAMES.get(lang, LANG_NAMES['en'])}.\n<question>{question}</question>"
    )
    result = ai.extract(AskAnswer, system=ASK_SYSTEM, prompt=prompt, max_tokens=1200, effort="medium")

    by_ref = {c.ref: c for c in found}
    citations, seen = [], set()
    for cit in result.citations:
        clause = by_ref.get(cit.ref.strip().lstrip("§"))
        if clause is None or clause.ref in seen:
            continue  # the model cited a clause it wasn't given: drop it
        seen.add(clause.ref)
        quote = cit.quote.strip().strip('"“”')
        if not quote or _norm(quote) not in _norm(clause.text):
            quote = best_sentence(clause.text, f"{question} {result.answer}")  # only show words that are really in the policy
        citations.append({"ref": clause.ref, "title": clause.title, "quote": quote, "clause_id": clause.id})

    answer_type = result.answer_type
    if answer_type == "answered" and not citations:
        answer_type = "needs_more_info"  # an answer that can't point to a clause isn't presented as settled
    return AskResult(answer_type, result.answer.strip(), citations, [f.strip() for f in result.follow_ups if f.strip()][:3], "ai")
