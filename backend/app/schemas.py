from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Language = Literal["en", "hi", "hn"]


class SignupIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    preferred_language: Language = "en"


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    preferred_language: Language


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    preferred_language: Language | None = None


class PolicyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    name: str
    insurer: str
    policy_number: str | None
    status: str
    sum_insured: int | None
    cover_since: date | None
    renews_on: date | None
    highlights: dict
    auto_created: bool = False
    analysis_status: Literal["none", "running", "ready", "failed"] = "none"
    analysis_mode: Literal["ai", "basic"] | None = None
    analyzed_at: datetime | None = None
    clause_count: int = 0


class PolicyDetailOut(PolicyOut):
    terms: dict | None = None  # understanding.terms.PolicyTerms
    timeline: dict | None = None  # rules.coverage.policy_timeline


ClauseCategory = Literal["coverage", "exclusion", "limit", "waiting_period", "definition", "condition", "claim_process", "grievance", "other"]


class ClauseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ref: str
    title: str
    section_title: str
    text: str
    category: ClauseCategory
    plain: dict | None  # {"en", "hi", "hn"}; None in basic mode
    page_start: int
    page_end: int
    document_id: int | None


class ClauseHit(BaseModel):
    clause: ClauseOut
    score: float


class AskIn(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    lang: Language = "en"


class CompareIn(BaseModel):
    a: int
    b: int
    scenario: str | None = Field(default=None, description="key of a preset situation")
    custom: str | None = Field(default=None, min_length=3, max_length=300, description="a situation in the user's own words")
    lang: Language = "en"


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Literal["user", "assistant"]
    content: str
    lang: str
    answer_type: str | None
    citations: list[dict]
    follow_ups: list[str]
    mode: str | None
    created_at: datetime


DocumentKind = Literal[
    # policy documents
    "policy_wording",
    "policy_schedule",
    "endorsement",
    "previous_policy",
    # claim documents
    "rejection_letter",
    "renewal_receipt",
    "discharge_summary",
    "hospital_bill",
    "doctor_note",
    "other",
]


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_id: int | None
    kind: DocumentKind
    filename: str
    content_type: str
    size_bytes: int
    status: Literal["processing", "ready", "failed"]
    error: str | None
    page_count: int | None
    ocr_pages: int
    suggested_kind: DocumentKind | None = None
    created_at: datetime


class DocumentUpdate(BaseModel):
    kind: DocumentKind


class DocumentPageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page_number: int
    text: str
    method: Literal["text", "ocr"]
    ocr_confidence: float | None
