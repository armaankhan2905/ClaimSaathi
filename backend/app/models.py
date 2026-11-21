from datetime import date, datetime, timezone

from sqlalchemy import JSON, BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy import func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from .db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    preferred_language: Mapped[str] = mapped_column(String(8), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    policies: Mapped[list["Policy"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Policy(Base):
    """A policy saved by a user, with what ClaimSaathi understood from its documents."""

    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(20))  # health | motor | life | travel | other
    name: Mapped[str] = mapped_column(String(160))
    insurer: Mapped[str] = mapped_column(String(160))
    policy_number: Mapped[str | None] = mapped_column(String(80), default=None)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | lapsed | processing
    sum_insured: Mapped[int | None] = mapped_column(BigInteger, default=None)  # rupees; IDV for motor
    cover_since: Mapped[date | None] = mapped_column(Date, default=None)  # first policy date (for waiting periods)
    renews_on: Mapped[date | None] = mapped_column(Date, default=None)
    highlights: Mapped[dict] = mapped_column(JSON, default=dict)  # e.g. {"addons": [...], "warnings": [...]}
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # Filled by policy understanding (Stage 2)
    terms: Mapped[dict | None] = mapped_column(JSON, default=None)  # see understanding.terms.PolicyTerms
    analysis_status: Mapped[str] = mapped_column(String(20), default="none")  # none | running | ready | failed
    analysis_mode: Mapped[str | None] = mapped_column(String(10), default=None)  # ai | basic
    analysis_error: Mapped[str | None] = mapped_column(String(200), default=None)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    auto_created: Mapped[bool] = mapped_column(Boolean, default=False)  # made from an upload, details still being read

    owner: Mapped[User] = relationship(back_populates="policies")
    documents: Mapped[list["Document"]] = relationship(back_populates="policy", cascade="all, delete-orphan")
    clauses: Mapped[list["Clause"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan", order_by="Clause.order"
    )
    chat: Mapped[list["ChatMessage"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan", order_by="ChatMessage.id"
    )


class Clause(Base):
    """One numbered clause of a policy, with its category and plain-language explanation."""

    __tablename__ = "clauses"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("policies.id", ondelete="CASCADE"), index=True)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), default=None)
    order: Mapped[int] = mapped_column(Integer)
    ref: Mapped[str] = mapped_column(String(20))  # "4.2"
    title: Mapped[str] = mapped_column(String(200))
    section_title: Mapped[str] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(Text)
    page_start: Mapped[int] = mapped_column(Integer)
    page_end: Mapped[int] = mapped_column(Integer)
    # coverage | exclusion | limit | waiting_period | definition | condition | claim_process | grievance | other
    category: Mapped[str] = mapped_column(String(20), default="other")
    plain: Mapped[dict | None] = mapped_column(JSON, default=None)  # {"en": "...", "hi": "...", "hn": "..."}
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary, default=None)  # float32 vector

    policy: Mapped[Policy] = relationship(back_populates="clauses")


class Document(Base):
    """An uploaded file (policy wording, schedule, rejection letter, bill...). Stored encrypted."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    policy_id: Mapped[int | None] = mapped_column(ForeignKey("policies.id", ondelete="CASCADE"), index=True, default=None)
    kind: Mapped[str] = mapped_column(String(30))  # see schemas.DocumentKind
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(60))  # application/pdf | image/jpeg | image/png | image/webp
    size_bytes: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64))
    storage_key: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default="processing")  # processing | ready | failed
    error: Mapped[str | None] = mapped_column(String(80), default=None)  # machine-readable reason when failed
    page_count: Mapped[int | None] = mapped_column(Integer, default=None)
    ocr_pages: Mapped[int] = mapped_column(Integer, default=0)
    suggested_kind: Mapped[str | None] = mapped_column(String(30), default=None)  # what the text looks like
    claim_id: Mapped[int | None] = mapped_column(ForeignKey("claims.id", ondelete="CASCADE"), index=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    owner: Mapped[User] = relationship(back_populates="documents")
    policy: Mapped[Policy | None] = relationship(back_populates="documents")
    claim: Mapped["Claim | None"] = relationship(back_populates="documents")
    pages: Mapped[list["DocumentPage"]] = relationship(
        back_populates="document", cascade="all, delete-orphan", order_by="DocumentPage.page_number"
    )


class Claim(Base):
    """A rejected (or disputed) claim being checked against its policy."""

    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    policy_id: Mapped[int | None] = mapped_column(ForeignKey("policies.id", ondelete="SET NULL"), index=True, default=None)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft | checking | ready | failed
    error: Mapped[str | None] = mapped_column(String(80), default=None)
    lang: Mapped[str] = mapped_column(String(4), default="en")  # language the AI explanations were written in
    mode: Mapped[str | None] = mapped_column(String(10), default=None)  # ai | basic
    facts: Mapped[dict | None] = mapped_column(JSON, default=None)  # what the rejection letter says (understanding.claims.LetterFacts)
    findings: Mapped[dict | None] = mapped_column(JSON, default=None)  # assessment, evidence map, timeline, checklist, questions
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    documents: Mapped[list[Document]] = relationship(back_populates="claim", cascade="all, delete-orphan")
    policy: Mapped[Policy | None] = relationship()


class Complaint(Base):
    """A complaint about a claim, moving from the insurer to Bima Bharosa to the Ombudsman."""

    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    claim_id: Mapped[int | None] = mapped_column(ForeignKey("claims.id", ondelete="SET NULL"), index=True, default=None)
    stage: Mapped[str] = mapped_column(String(20), default="insurer")  # insurer | bima_bharosa | ombudsman
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft | sent | resolved
    fields: Mapped[dict] = mapped_column(JSON, default=dict)  # the editable letter details (see complaints.prefill)
    history: Mapped[list] = mapped_column(JSON, default=list)  # [{"kind": created|sent|reply|escalated|resolved, "stage", "date", ...}]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    claim: Mapped[Claim | None] = relationship()


class DocumentPage(Base):
    """Clean text of one page, either read directly from the PDF or produced by OCR."""

    __tablename__ = "document_pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    page_number: Mapped[int] = mapped_column(Integer)  # 1-based
    text: Mapped[str] = mapped_column(Text)
    method: Mapped[str] = mapped_column(String(10))  # text | ocr
    ocr_confidence: Mapped[float | None] = mapped_column(Float, default=None)  # average, 0..1

    document: Mapped[Document] = relationship(back_populates="pages")


class ChatMessage(Base):
    """One turn of "Ask ClaimSaathi" about a policy (kept so the conversation survives a reload)."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("policies.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(10))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    lang: Mapped[str] = mapped_column(String(4), default="en")
    answer_type: Mapped[str | None] = mapped_column(String(20), default=None)  # assistant only
    citations: Mapped[list] = mapped_column(JSON, default=list)  # [{"ref", "title", "quote", "clause_id"}]
    follow_ups: Mapped[list] = mapped_column(JSON, default=list)
    mode: Mapped[str | None] = mapped_column(String(10), default=None)  # ai | basic
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    policy: Mapped[Policy] = relationship(back_populates="chat")


# Number of clauses, loaded with the policy in one query (shown on cards and lists).
Policy.clause_count = column_property(
    select(func.count(Clause.id)).where(Clause.policy_id == Policy.id).correlate_except(Clause).scalar_subquery()
)
