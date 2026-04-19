from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class CreateOperatorRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    business_name: str
    business_phone: str


class OperatorProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    business_name: str
    phone: str
    is_approved: bool
    approved_at: Optional[datetime]
    created_at: datetime


class CreateDriverRequest(BaseModel):
    name: str
    phone: str
    licence_number: Optional[str] = None
    linked_user_id: Optional[UUID] = None


class DriverResponse(BaseModel):
    id: UUID
    operator_id: UUID
    name: str
    phone: str
    licence_number: Optional[str]
    linked_user_id: Optional[UUID]
    is_active: bool
    created_at: datetime