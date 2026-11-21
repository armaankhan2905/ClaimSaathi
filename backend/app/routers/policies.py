from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ..db import get_db, get_session_factory
from ..deps import current_user
from ..documents import delete_document_files
from ..models import Policy, User
from ..rules.coverage import policy_timeline
from ..schemas import ClauseHit, ClauseOut, PolicyDetailOut, PolicyOut
from ..understanding.pipeline import understand_policy
from ..understanding.search import SearchDoc, clause_search_text, from_bytes, search
from ..understanding.terms import PolicyTerms

router = APIRouter(prefix="/api/policies", tags=["policies"])


def get_owned_policy(policy_id: int, user: User, db: Session) -> Policy:
    policy = db.get(Policy, policy_id)
    if policy is None or policy.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "policy_not_found")
    return policy


@router.get("", response_model=list[PolicyOut])
def list_policies(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Policy]:
    return list(db.scalars(select(Policy).where(Policy.owner_id == user.id).order_by(Policy.created_at, Policy.id)))


@router.get("/{policy_id}", response_model=PolicyDetailOut)
def get_policy(policy_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> PolicyDetailOut:
    policy = get_owned_policy(policy_id, user, db)
    out = PolicyDetailOut.model_validate(policy)
    if policy.terms:
        out.terms = policy.terms
        out.timeline = policy_timeline(PolicyTerms.model_validate(policy.terms))  # computed fresh: "days left" changes daily
    return out


@router.get("/{policy_id}/clauses", response_model=list[ClauseOut])
def list_clauses(policy_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return get_owned_policy(policy_id, user, db).clauses


@router.get("/{policy_id}/search", response_model=list[ClauseHit])
def search_clauses(
    policy_id: int,
    q: str = Query(min_length=1, max_length=500),
    k: int = Query(5, ge=1, le=20),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> list[ClauseHit]:
    """The clauses most relevant to a question (English, Hindi or Hinglish)."""
    clauses = get_owned_policy(policy_id, user, db).clauses
    docs = [
        SearchDoc(i, c.ref, clause_search_text(c.ref, c.title, c.section_title, c.text), from_bytes(c.embedding) if c.embedding else None)
        for i, c in enumerate(clauses)
    ]
    return [ClauseHit(clause=ClauseOut.model_validate(clauses[i]), score=round(score, 3)) for i, score in search(q, docs, k)]


@router.post("/{policy_id}/analyze", response_model=PolicyOut, status_code=status.HTTP_202_ACCEPTED)
def analyze_policy(
    policy_id: int,
    background: BackgroundTasks,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    session_factory: sessionmaker = Depends(get_session_factory),
) -> Policy:
    """Read the policy's documents again (e.g. after adding an API key)."""
    policy = get_owned_policy(policy_id, user, db)
    policy.analysis_status = "running"
    db.commit()
    background.add_task(understand_policy, policy.id, session_factory)
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(policy_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    policy = get_owned_policy(policy_id, user, db)
    delete_document_files(policy.documents)  # its uploaded files go too, not just the database rows
    db.delete(policy)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
