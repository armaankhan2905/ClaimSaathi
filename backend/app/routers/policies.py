from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_user
from ..documents import delete_document_files
from ..models import Policy, User
from ..schemas import PolicyOut

router = APIRouter(prefix="/api/policies", tags=["policies"])


def get_owned_policy(policy_id: int, user: User, db: Session) -> Policy:
    policy = db.get(Policy, policy_id)
    if policy is None or policy.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "policy_not_found")
    return policy


@router.get("", response_model=list[PolicyOut])
def list_policies(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Policy]:
    return list(db.scalars(select(Policy).where(Policy.owner_id == user.id).order_by(Policy.created_at, Policy.id)))


@router.get("/{policy_id}", response_model=PolicyOut)
def get_policy(policy_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Policy:
    return get_owned_policy(policy_id, user, db)


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(policy_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    policy = get_owned_policy(policy_id, user, db)
    delete_document_files(policy.documents)  # its uploaded files go too, not just the database rows
    db.delete(policy)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
