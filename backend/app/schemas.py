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
    created_at: datetime


class DocumentPageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page_number: int
    text: str
    method: Literal["text", "ocr"]
    ocr_confidence: float | None
