import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class OTPRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if not cleaned.startswith("62") or len(cleaned) < 10:
            raise ValueError(
                "Phone must be a valid Indonesian number starting with 62"
            )
        return cleaned


class OTPVerify(BaseModel):
    phone: str
    otp_code: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if not cleaned.startswith("62") or len(cleaned) < 10:
            raise ValueError("Invalid phone number")
        return cleaned


class PasswordLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str