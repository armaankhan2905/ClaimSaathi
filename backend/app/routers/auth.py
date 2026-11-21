from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_user
from ..models import User
from ..schemas import LoginIn, SignupIn, TokenOut, UserOut, UserUpdate
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _find_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(func.lower(User.email) == email.lower()))


@router.post("/signup", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def signup(body: SignupIn, db: Session = Depends(get_db)) -> TokenOut:
    if _find_by_email(db, body.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")
    user = User(
        email=body.email.lower(),
        full_name=body.full_name.strip(),
        password_hash=hash_password(body.password),
        preferred_language=body.preferred_language,
    )
    db.add(user)
    db.commit()
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = _find_by_email(db, body.email)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password")
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> User:
    return user


@router.patch("/me", response_model=UserOut)
def update_me(body: UserUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> User:
    if body.full_name is not None:
        user.full_name = body.full_name.strip()
    if body.preferred_language is not None:
        user.preferred_language = body.preferred_language
    db.add(user)
    db.commit()
    return user
