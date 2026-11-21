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
