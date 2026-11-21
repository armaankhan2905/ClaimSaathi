from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from ..claims_pipeline import effective_kind, run_check
from ..db import get_db, get_session_factory
from ..deps import current_user
from ..documents import delete_document_files
from ..models import Claim, Complaint, User
from ..report import build_report
from ..schemas import CheckIn, ClaimIn, ClaimOut, ClaimUpdate
from .policies import get_owned_policy

router = APIRouter(prefix="/api/claims", tags=["rejection check"])


def get_owned_claim(claim_id: int, user: User, db: Session) -> Claim:
    claim = db.get(Claim, claim_id)
    if claim is None or claim.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "claim_not_found")
    return claim


@router.post("", response_model=ClaimOut, status_code=status.HTTP_201_CREATED)
def create_claim(body: ClaimIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Claim:
    if body.policy_id is not None:
        get_owned_policy(body.policy_id, user, db)
    claim = Claim(owner_id=user.id, policy_id=body.policy_id, lang=body.lang)
    db.add(claim)
    db.commit()
    return claim


@router.get("", response_model=list[ClaimOut])
def list_claims(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Claim]:
    return list(db.scalars(select(Claim).where(Claim.owner_id == user.id).order_by(Claim.created_at.desc(), Claim.id.desc())))


@router.get("/{claim_id}", response_model=ClaimOut)
def get_claim(claim_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Claim:
    return get_owned_claim(claim_id, user, db)


@router.patch("/{claim_id}", response_model=ClaimOut)
def update_claim(claim_id: int, body: ClaimUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Claim:
    claim = get_owned_claim(claim_id, user, db)
    if body.policy_id is not None:
        get_owned_policy(body.policy_id, user, db)
    claim.policy_id = body.policy_id
    db.commit()
    return claim


@router.post("/{claim_id}/check", response_model=ClaimOut, status_code=status.HTTP_202_ACCEPTED)
def check(
    claim_id: int,
    body: CheckIn,
    background: BackgroundTasks,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    session_factory: sessionmaker = Depends(get_session_factory),
) -> Claim:
    """Check the rejection against the policy (runs in the background; poll GET until it's ready)."""
    claim = get_owned_claim(claim_id, user, db)
    if any(d.status == "processing" for d in claim.documents):
        raise HTTPException(status.HTTP_409_CONFLICT, "documents_still_reading")
    if not any(d.status == "ready" and effective_kind(d) == "rejection_letter" for d in claim.documents):
        raise HTTPException(status.HTTP_409_CONFLICT, "no_letter")
    claim.status, claim.error, claim.lang = "checking", None, body.lang
    db.commit()
    background.add_task(run_check, claim.id, session_factory)
    return claim


@router.get("/{claim_id}/report")
def report(claim_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    claim = get_owned_claim(claim_id, user, db)
    if claim.status != "ready" or not claim.findings:
        raise HTTPException(status.HTTP_409_CONFLICT, "not_checked")
    pdf = build_report(claim, claim.policy)
    name = f"ClaimSaathi-evidence-{(claim.facts or {}).get('claim_number') or claim.id}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{name}"', "Cache-Control": "private, no-store"},
    )


@router.delete("/{claim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_claim(claim_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    claim = get_owned_claim(claim_id, user, db)
    delete_document_files(claim.documents)  # the claim's uploaded files go too
    db.execute(update(Complaint).where(Complaint.claim_id == claim.id).values(claim_id=None))  # complaints stay, unlinked
    db.delete(claim)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
