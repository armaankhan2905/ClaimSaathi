"""Create the fictional demo account and sample policies.

Run from the backend folder:  python -m app.seed
Add --with-documents to also load the sample PDFs and the letter photo from samples/ into the
demo account and read them (takes a few minutes with the Groq free plan; instant in basic mode).
Safe to run more than once. All names, insurers and numbers here are made up.
"""

import hashlib
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import storage
from .config import BASE_DIR, get_settings
from .db import SessionLocal, init_db
from .documents import process_document
from .extraction.reader import sniff_content_type
from .models import Document, Policy, User
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


SAMPLES = BASE_DIR.parent / "samples"
# (file, document type, policy number to attach it to; None = let ClaimSaathi create/find the policy)
SAMPLE_DOCUMENTS = [
    ("suraksha-health-plus-policy-wording.pdf", "policy_wording", "NGI/HL/2026/448812"),
    ("suraksha-health-plus-policy-schedule.pdf", "policy_schedule", "NGI/HL/2026/448812"),
    ("drivesure-comprehensive-policy-wording.pdf", "policy_wording", "KMI/PC/2026/091174"),
    ("arogya-secure-gold-policy-wording.pdf", "policy_wording", None),
    ("arogya-secure-gold-policy-schedule.pdf", "policy_schedule", None),
    ("rejection-letter-CLM-26-08817-photo.jpg", "rejection_letter", None),
]


def load_sample_documents(user_id: int, session_factory=SessionLocal, samples: Path = SAMPLES) -> int:
    """Upload and read the sample files for the demo account (skips ones already there)."""
    added = 0
    for name, kind, policy_number in SAMPLE_DOCUMENTS:
        path = samples / name
        if not path.exists():
            print(f"  missing {path} (run scripts/make_sample_docs.py)")
            continue
        data = path.read_bytes()
        with session_factory() as db:
            digest = hashlib.sha256(data).hexdigest()
            if db.scalar(select(Document).where(Document.owner_id == user_id, Document.sha256 == digest)):
                continue
            policy = db.scalar(select(Policy).where(Policy.owner_id == user_id, Policy.policy_number == policy_number)) if policy_number else None
            doc = Document(
                owner_id=user_id, policy_id=policy.id if policy else None, kind=kind, filename=name,
                content_type=sniff_content_type(data) or "application/pdf", size_bytes=len(data), sha256=digest,
                storage_key=storage.save(data), status="processing",
            )
            db.add(doc)
            db.commit()
            doc_id = doc.id
        print(f"  reading {name} ...", flush=True)
        process_document(doc_id, session_factory)
        added += 1
    return added


if __name__ == "__main__":
    init_db()
    with SessionLocal() as session:
        u = seed(session)
        print(f"Demo account ready: {u.email} with {len(u.policies)} sample policies")
    if "--with-documents" in sys.argv:
        print(f"Loaded {load_sample_documents(u.id)} sample documents")
