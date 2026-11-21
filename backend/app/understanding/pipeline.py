"""From read documents to an understood policy.

after_document_read  - runs when a document's text is ready: suggests its type and, for policy
                       documents, makes sure it belongs to a policy, then understands that policy.
understand_policy    - splits clauses, extracts terms, labels and embeds clauses, updates the
                       policy card, and merges duplicate cards of the same policy.
"""

import logging
import re
import threading
from collections import defaultdict
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ..ai import get_ai
from ..models import Clause, Document, Policy
from ..rules.coverage import continuous_cover
from .clauses import split_clauses
from .dates import parse_date
from .kinds import is_policy_document, suggest_kind
from .labels import label_clauses
from .search import clause_search_text, embed, to_bytes
from .terms import PolicyTerms, extract_terms

log = logging.getLogger(__name__)
# One user's policies are understood one at a time, so two uploads finishing together can't
# both try to merge into each other.
_owner_locks: dict[int, threading.Lock] = defaultdict(threading.Lock)


def _doc_text(doc: Document) -> str:
    return "\n\n".join(p.text for p in doc.pages)


def _name_from_filename(filename: str) -> str:
    stem = re.sub(r"\.[a-z0-9]{2,4}$", "", filename, flags=re.I)
    stem = re.sub(r"[-_]+", " ", stem).strip()
    stem = re.sub(r"\b(policy )?(wording|schedule|scanned|copy|final)\b", "", stem, flags=re.I).strip()
    return (stem[:1].upper() + stem[1:])[:160] or "New policy"


def after_document_read(document_id: int, session_factory: sessionmaker) -> None:
    with session_factory() as db:
        doc = db.get(Document, document_id)
        if doc is None or doc.status != "ready":
            return
        doc.suggested_kind = suggest_kind(_doc_text(doc))
        if is_policy_document(doc.kind, doc.suggested_kind) and doc.policy_id is None:
            policy = Policy(
                owner_id=doc.owner_id,
                category="other",
                name=_name_from_filename(doc.filename),
                insurer="",
                status="processing",
                auto_created=True,
                highlights={},
            )
            db.add(policy)
            db.flush()
            doc.policy_id = policy.id
        db.commit()
        policy_id = doc.policy_id
    if policy_id is not None:
        understand_policy(policy_id, session_factory)


def understand_policy(policy_id: int, session_factory: sessionmaker) -> None:
    with session_factory() as db:
        owner_id = db.scalar(select(Policy.owner_id).where(Policy.id == policy_id))
    if owner_id is None:
        return
    target_id = None
    with _owner_locks[owner_id]:
        with session_factory() as db:
            policy = db.get(Policy, policy_id)
            if policy is None:
                return
            docs = [d for d in policy.documents if is_policy_document(d.kind, d.suggested_kind)]
            if any(d.status == "processing" for d in docs):
                return  # runs again when the last one is read
            docs = sorted((d for d in docs if d.status == "ready"), key=lambda d: (d.created_at, d.id))
            if not docs:
                policy.clauses = []
                policy.terms = None
                policy.analysis_status = "none"
                if policy.auto_created:
                    db.delete(policy)  # its only documents were removed or turned out not to be policy documents
                db.commit()
                return
            policy.analysis_status = "running"
            db.commit()
            try:
                target_id = _analyse(db, policy, docs)
            except Exception:
                log.exception("Understanding policy %s failed", policy_id)
                db.rollback()
                policy = db.get(Policy, policy_id)
                if policy is not None:
                    policy.analysis_status = "failed"
                    policy.analysis_error = "internal_error"
                    if policy.status == "processing":
                        policy.status = "active"
                    db.commit()
                return
    if target_id is not None:  # merged into an existing card: understand that one with all documents
        understand_policy(target_id, session_factory)


def _analyse(db: Session, policy: Policy, docs: list[Document]) -> int | None:
    ai = get_ai()
    schedule_text = "\n\n".join(_doc_text(d) for d in docs if d.kind in ("policy_schedule", "previous_policy"))
    wording_docs = [d for d in docs if d.kind in ("policy_wording", "endorsement")]
    wording_text = "\n\n".join(_doc_text(d) for d in wording_docs)

    split = []
    owner_doc = []
    for d in wording_docs:
        for c in split_clauses([(p.page_number, p.text) for p in d.pages]):
            split.append(c)
            owner_doc.append(d.id)
    for i, c in enumerate(split):
        c.order = i

    terms, terms_mode = extract_terms(schedule_text, wording_text, split, ai)

    # A card made from an upload may duplicate one the user already has: same number, or same plan and insurer.
    if policy.auto_created:
        twin = _find_twin(db, policy, terms)
        if twin is not None:
            # Move through the relationship: the documents get a new parent instead of being
            # treated as orphans and deleted along with this card.
            for d in list(policy.documents):
                d.policy = twin
            db.delete(policy)
            db.commit()
            return twin.id

    labels, label_mode = label_clauses(split, ai)
    vectors = embed([clause_search_text(c.ref, c.title, c.section_title, c.text) for c in split])

    policy.clauses = [
        Clause(
            document_id=owner_doc[i],
            order=c.order,
            ref=c.ref,
            title=c.title[:200],
            section_title=c.section_title[:200],
            text=c.text,
            page_start=c.page_start,
            page_end=c.page_end,
            category=labels[i][0],
            plain=labels[i][1],
            embedding=to_bytes(vectors[i]) if vectors is not None else None,
        )
        for i, c in enumerate(split)
    ]
    _apply_terms(policy, terms)
    policy.terms = terms.model_dump()
    policy.analysis_mode = "ai" if "ai" in (terms_mode, label_mode) else "basic"
    policy.analysis_status = "ready"
    policy.analysis_error = None
    policy.analyzed_at = datetime.now(timezone.utc)
    db.commit()
    return None


def _norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _find_twin(db: Session, policy: Policy, terms: PolicyTerms) -> Policy | None:
    others = db.scalars(select(Policy).where(Policy.owner_id == policy.owner_id, Policy.id != policy.id).order_by(Policy.id)).all()
    for other in others:
        if terms.policy_number and _norm(other.policy_number) == _norm(terms.policy_number):
            return other
    for other in others:
        same_plan = terms.policy_name and _norm(other.name) == _norm(terms.policy_name)
        same_insurer = not terms.insurer or not other.insurer or _norm(terms.insurer).startswith(_norm(other.insurer)) or _norm(other.insurer).startswith(_norm(terms.insurer))
        if same_plan and same_insurer:
            return other
    return None


def _apply_terms(policy: Policy, terms: PolicyTerms) -> None:
    """The documents are the source of truth: copy every value they state onto the card."""
    if terms.policy_name:
        policy.name = terms.policy_name[:160]
    if terms.insurer:
        policy.insurer = terms.insurer[:160]
    if terms.category:
        policy.category = terms.category
    if terms.policy_number:
        policy.policy_number = terms.policy_number[:80]
    if terms.sum_insured:
        policy.sum_insured = terms.sum_insured
    since = parse_date(continuous_cover(terms).continuous_since) or parse_date(terms.first_policy_date)
    if since:
        policy.cover_since = since
    end = parse_date(terms.policy_end)
    if end:
        policy.renews_on = end
    if terms.addons:
        policy.highlights = {**(policy.highlights or {}), "addons": terms.addons}
    if policy.status == "processing" or end:
        policy.status = "lapsed" if end and end < date.today() else "active"
    if terms.policy_name:
        policy.auto_created = False  # it has a real name now, so it's no longer a placeholder
