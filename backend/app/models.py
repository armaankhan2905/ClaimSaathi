from datetime import date, datetime, timezone

from sqlalchemy import JSON, BigInteger, Date, DateTime, ForeignKey, String
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
