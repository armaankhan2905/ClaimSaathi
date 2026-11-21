"""Background work for a Rejection Check: gather the claim's documents and the policy, run the check."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from .ai import get_ai
from .models import Claim, Policy
from .understanding.ask import ClauseView
from .understanding.claims import check_claim

log = logging.getLogger(__name__)


def _text(doc) -> str:
    return "\n\n".join(p.text for p in doc.pages)


def effective_kind(doc) -> str:
    """What a claim document really is: its label, unless the text clearly says it's a rejection letter."""
    if doc.suggested_kind == "rejection_letter":
        return "rejection_letter"
    return doc.kind


def run_check(claim_id: int, session_factory: sessionmaker) -> None:
    with session_factory() as db:
        claim = db.get(Claim, claim_id)
        if claim is None:
            return
        try:
            ready = [d for d in claim.documents if d.status == "ready"]
            letters = [d for d in ready if effective_kind(d) == "rejection_letter"]
            if not letters:
                claim.status, claim.error = "failed", "no_letter"
                db.commit()
                return
            others: dict[str, list[str]] = {}
            for d in ready:
                if d not in letters:
                    others.setdefault(effective_kind(d), []).append(_text(d))

            policy = db.get(Policy, claim.policy_id) if claim.policy_id else None
            clauses = [ClauseView(c.id, c.ref, c.title, c.section_title, c.text, c.category, c.plain, c.embedding) for c in policy.clauses] if policy else []
            has_wording = bool(policy and any(d.kind == "policy_wording" and d.status == "ready" for d in policy.documents))
            facts, findings, mode = check_claim(
                "\n\n".join(_text(d) for d in letters), others, policy.terms if policy else None, clauses, has_wording, claim.lang, get_ai()
            )

            # No policy chosen yet: find it by the policy number in the letter.
            if policy is None and facts.get("policy_number"):
                match = db.scalar(select(Policy).where(Policy.owner_id == claim.owner_id, Policy.policy_number == facts["policy_number"]))
                if match is not None:
                    claim.policy_id = match.id
                    db.commit()
                    return run_check(claim_id, session_factory)

            claim.facts, claim.findings, claim.mode = facts, findings, mode
            claim.status = "ready"
            claim.error = None if policy else "no_policy"  # checked, but without a policy to compare against
            claim.checked_at = datetime.now(timezone.utc)
            db.commit()
        except Exception:
            log.exception("Rejection check %s failed", claim_id)
            db.rollback()
            claim = db.get(Claim, claim_id)
            if claim is not None:
                claim.status, claim.error = "failed", "internal_error"
                db.commit()

