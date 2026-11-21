from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import complaints as cp
from ..complaint_pdf import letter_pdf, package_pdf
from ..db import get_db
from ..deps import current_user
from ..models import Complaint, Document, User
from ..report import build_report
from ..schemas import ComplaintIn, ComplaintOut, ComplaintUpdate, EscalateIn, ReplyIn, SentIn
from .claims import get_owned_claim

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def get_owned_complaint(complaint_id: int, user: User, db: Session) -> Complaint:
    c = db.get(Complaint, complaint_id)
    if c is None or c.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "complaint_not_found")
    return c


def candidate_documents(c_claim, db: Session, user: User) -> list[Document]:
    """Documents that can go with the complaint: the claim's own, then its policy's."""
    if c_claim is None:
        return []
    docs = [d for d in c_claim.documents if d.status == "ready"]
    if c_claim.policy_id:
        docs += list(db.scalars(select(Document).where(Document.policy_id == c_claim.policy_id, Document.owner_id == user.id, Document.status == "ready")))
    seen, out = set(), []
    for d in docs:
        if d.id not in seen:
            seen.add(d.id)
            out.append(d)
    return out


def _letter(c: Complaint, docs: list[Document], has_report: bool) -> dict:
    """The letter for the current stage, dated the day it was sent (or today while it's a draft)."""
    sent = cp.last_event(c.history, "sent", c.stage) if c.status != "draft" else None
    return cp.build_letter(c.stage, c.fields, c.history, docs, has_report, date.fromisoformat(sent["date"]) if sent else None)


def _has_report(c: Complaint) -> bool:
    return bool(c.claim and c.claim.status == "ready" and c.claim.findings)


def to_out(c: Complaint, db: Session, user: User) -> ComplaintOut:
    docs = candidate_documents(c.claim, db, user)
    has_report = _has_report(c)
    letter = _letter(c, docs, has_report)
    return ComplaintOut(
        id=c.id,
        claim_id=c.claim_id,
        stage=c.stage,
        status=c.status,
        fields=c.fields,
        history=c.history,
        recommended_stage=cp.recommended_stage(c.fields),
        tracker=cp.tracker(c.stage, c.status, c.fields, c.history),
        letter=letter,
        letter_text=cp.letter_text(letter),
        attachment_options=[{"id": d.id, "filename": d.filename, "kind": d.kind} for d in docs],
        has_report=has_report,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def _event(c: Complaint, kind: str, **extra) -> None:
    c.history = [*(c.history or []), {"kind": kind, "stage": c.stage, "date": extra.pop("on", None) or date.today().isoformat(), **extra}]


@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
def create_complaint(body: ComplaintIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ComplaintOut:
    claim = get_owned_claim(body.claim_id, user, db) if body.claim_id is not None else None
    fields = cp.prefill(user, claim, claim.policy if claim else None, candidate_documents(claim, db, user))
    fields["situation"] = body.situation
    c = Complaint(owner_id=user.id, claim_id=claim.id if claim else None, stage=cp.SITUATIONS[body.situation], fields=fields, history=[])
    _event(c, "created")
    db.add(c)
    db.commit()
    return to_out(c, db, user)


@router.get("", response_model=list[ComplaintOut])
def list_complaints(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[ComplaintOut]:
    rows = db.scalars(select(Complaint).where(Complaint.owner_id == user.id).order_by(Complaint.created_at.desc(), Complaint.id.desc()))
    return [to_out(c, db, user) for c in rows]


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ComplaintOut:
    return to_out(get_owned_complaint(complaint_id, user, db), db, user)


@router.patch("/{complaint_id}", response_model=ComplaintOut)
def update_complaint(complaint_id: int, body: ComplaintUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ComplaintOut:
    """Save edits to the letter details, or pick where to file (only before it is sent)."""
    c = get_owned_complaint(complaint_id, user, db)
    if body.fields:
        allowed = {d.id for d in candidate_documents(c.claim, db, user)}
        fields = cp.clean_fields(c.fields, body.fields)
        fields["attachments"] = [i for i in fields.get("attachments") or [] if i in allowed]
        c.fields = fields
    if body.stage and body.stage != c.stage:
        if c.status != "draft":
            raise HTTPException(status.HTTP_409_CONFLICT, "already_sent")
        c.stage = body.stage
    db.commit()
    return to_out(c, db, user)


@router.post("/{complaint_id}/sent", response_model=ComplaintOut)
def mark_sent(complaint_id: int, body: SentIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ComplaintOut:
    """The user has sent the letter themselves (by e-mail, post or the portal)."""
    c = get_owned_complaint(complaint_id, user, db)
    if c.status != "draft":
        raise HTTPException(status.HTTP_409_CONFLICT, "already_sent")
    sent_on = body.sent_on or date.today()
    if sent_on > date.today():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "date_in_future")
    c.status = "sent"
    _event(c, "sent", on=sent_on.isoformat(), reference=body.reference.strip())
    db.commit()
    return to_out(c, db, user)


@router.post("/{complaint_id}/reply", response_model=ComplaintOut)
def record_reply(complaint_id: int, body: ReplyIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ComplaintOut:
    c = get_owned_complaint(complaint_id, user, db)
    if c.status != "sent":
        raise HTTPException(status.HTTP_409_CONFLICT, "not_sent")
    reply_on = body.reply_on or date.today()
    _event(c, "reply", on=reply_on.isoformat(), outcome=body.outcome)
    if body.outcome == "resolved":
        c.status = "resolved"
        _event(c, "resolved", on=reply_on.isoformat())
    db.commit()
    return to_out(c, db, user)


@router.post("/{complaint_id}/escalate", response_model=ComplaintOut)
def escalate(complaint_id: int, body: EscalateIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ComplaintOut:
    """Take the complaint to the next level; a new draft is written for it."""
    c = get_owned_complaint(complaint_id, user, db)
    allowed = cp.tracker(c.stage, c.status, c.fields, c.history)["can_escalate"]
    if body.to not in allowed:
        raise HTTPException(status.HTTP_409_CONFLICT, "cannot_escalate_yet")
    _event(c, "escalated", to=body.to)
    c.stage, c.status = body.to, "draft"
    db.commit()
    return to_out(c, db, user)


def _pdf_response(content: bytes, name: str) -> Response:
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{name}"', "Cache-Control": "private, no-store"},
    )


def _file_stem(c: Complaint) -> str:
    claim_no = "".join(ch for ch in (c.fields.get("claim_number") or str(c.id)) if ch.isalnum() or ch in "-_")
    return f"ClaimSaathi-complaint-{c.stage.replace('_', '-')}-{claim_no}"


@router.get("/{complaint_id}/letter")
def download_letter(complaint_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    c = get_owned_complaint(complaint_id, user, db)
    letter = _letter(c, candidate_documents(c.claim, db, user), _has_report(c))
    return _pdf_response(letter_pdf(letter), f"{_file_stem(c)}.pdf")


@router.get("/{complaint_id}/package")
def download_package(complaint_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    """Letter, evidence report and the chosen documents, in one PDF ready to send."""
    c = get_owned_complaint(complaint_id, user, db)
    docs = candidate_documents(c.claim, db, user)
    has_report = _has_report(c)
    letter = _letter(c, docs, has_report)
    chosen = [d for d in docs if d.id in set(c.fields.get("attachments") or [])]
    report = build_report(c.claim, c.claim.policy) if has_report and c.fields.get("include_report") else None
    return _pdf_response(package_pdf(letter, report, chosen), f"{_file_stem(c)}-package.pdf")


@router.get("/{complaint_id}/reminder")
def download_reminder(complaint_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    c = get_owned_complaint(complaint_id, user, db)
    ics = cp.reminder_ics(c.id, c.stage, c.fields, cp.tracker(c.stage, c.status, c.fields, c.history))
    if ics is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "not_sent")
    return Response(
        content=ics,
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="{_file_stem(c)}-reminder.ics"', "Cache-Control": "private, no-store"},
    )


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_complaint(complaint_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    db.delete(get_owned_complaint(complaint_id, user, db))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
