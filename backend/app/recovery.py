"""Finish work that a restart interrupted.

Reading documents, understanding policies and checking rejections run in the background inside
the server process. If the server stops part-way (a closed window, a crash, a redeploy), their rows
stay "processing" / "running" / "checking" and the app would show "Reading…" for ever. On start-up
this picks them up again, in a background thread so start-up stays fast.
"""

import logging
import threading

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from .claims_pipeline import run_check
from .documents import process_document
from .models import Claim, Document, Policy
from .understanding.pipeline import understand_policy

log = logging.getLogger(__name__)


def resume_interrupted(session_factory: sessionmaker) -> None:
    with session_factory() as db:
        docs = db.scalars(select(Document.id).where(Document.status == "processing")).all()
        policies = db.scalars(select(Policy.id).where(Policy.analysis_status == "running")).all()
        claims = db.scalars(select(Claim.id).where(Claim.status == "checking")).all()
    if not (docs or policies or claims):
        return
    log.info("Resuming interrupted work: %s documents, %s policies, %s checks", len(docs), len(policies), len(claims))

    def work() -> None:
        for doc_id in docs:  # reading a document goes on to understand its policy
            process_document(doc_id, session_factory)
        for policy_id in policies:
            with session_factory() as db:
                still_running = db.scalar(select(Policy.analysis_status).where(Policy.id == policy_id)) == "running"
            if still_running:  # not already re-read as part of a resumed document above
                understand_policy(policy_id, session_factory)
        for claim_id in claims:
            run_check(claim_id, session_factory)

    threading.Thread(target=work, name="resume-interrupted", daemon=True).start()
