"""Create the fictional demo account and sample policies.

Run from the backend folder:  python -m app.seed
Safe to run more than once. All names, insurers and numbers here are made up.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .db import SessionLocal, init_db
from .models import Policy, User
from .security import hash_password

SAMPLE_POLICIES = [
    dict(
        category="health",
        name="Suraksha Health Plus",
        insurer="Navjeevan General Insurance",
        policy_number="NGI/HL/2026/448812",
        sum_insured=500_000,
        cover_since=date(2022, 3, 12),
        renews_on=date(2027, 3, 11),
        highlights={"addons": [], "warnings": []},
    ),
    dict(
        category="motor",
        name="DriveSure Comprehensive",
        insurer="Kavach Motor Insurance",
        policy_number="KMI/PC/2026/091174",
        sum_insured=640_000,
        cover_since=date(2024, 8, 5),
        renews_on=date(2027, 8, 4),
        highlights={"addons": ["Zero depreciation"], "warnings": ["No engine protect cover"]},
    ),
]


def seed(db: Session) -> User:
    s = get_settings()
    user = db.scalar(select(User).where(User.email == s.demo_email.lower()))
    if user is None:
        user = User(email=s.demo_email.lower(), full_name="Rohit Sharma (demo)", password_hash=hash_password(s.demo_password))
        db.add(user)
        db.flush()
    existing = {p.policy_number for p in user.policies}
    for data in SAMPLE_POLICIES:
        if data["policy_number"] not in existing:
            db.add(Policy(owner_id=user.id, **data))
    db.commit()
    db.refresh(user)
    return user


if __name__ == "__main__":
    init_db()
    with SessionLocal() as session:
        u = seed(session)
        print(f"Demo account ready: {u.email} with {len(u.policies)} sample policies")
