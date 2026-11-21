from datetime import date, datetime, timezone

from sqlalchemy import JSON, BigInteger, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    """A policy saved by a user. Clauses and documents are added in later stages."""

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

    owner: Mapped[User] = relationship(back_populates="policies")
    documents: Mapped[list["Document"]] = relationship(back_populates="policy", cascade="all, delete-orphan")


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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    owner: Mapped[User] = relationship(back_populates="documents")
    policy: Mapped[Policy | None] = relationship(back_populates="documents")
    pages: Mapped[list["DocumentPage"]] = relationship(
        back_populates="document", cascade="all, delete-orphan", order_by="DocumentPage.page_number"
    )


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
