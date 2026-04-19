import random
import string
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

OTP_TTL_MINUTES = 30


class ResolvedRole(str, Enum):
    PASSENGER = "passenger"
    OPERATOR  = "operator"
    ADMIN     = "admin"


class DomainError(Exception):
    pass


@dataclass
class OtpCode:
    phone: str
    code: str
    expires_at: datetime

    @classmethod
    def generate(cls, phone: str) -> "OtpCode":
        code = "".join(random.choices(string.digits, k=6))
        return cls(
            phone=phone,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES),
        )

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    def matches(self, candidate: str) -> bool:
        return self.code == candidate


@dataclass
class OperatorProfile:
    id: uuid.UUID
    user_id: uuid.UUID
    business_name: str
    phone: str
    is_approved: bool = False
    approved_at: Optional[datetime] = None
    approved_by_admin_id: Optional[uuid.UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls, user_id: uuid.UUID, business_name: str, phone: str
    ) -> "OperatorProfile":
        if not business_name.strip():
            raise DomainError("Business name cannot be empty")
        if not phone.strip():
            raise DomainError("Phone cannot be empty")
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            business_name=business_name.strip(),
            phone=phone.strip(),
        )

    def approve(self, admin_id: uuid.UUID) -> None:
        if self.is_approved:
            raise DomainError("Operator is already approved")
        self.is_approved = True
        self.approved_at = datetime.utcnow()
        self.approved_by_admin_id = admin_id

    def revoke(self) -> None:
        self.is_approved = False
        self.approved_at = None
        self.approved_by_admin_id = None


@dataclass
class Driver:
    id: uuid.UUID
    operator_id: uuid.UUID
    name: str
    phone: str
    licence_number: Optional[str] = None
    linked_user_id: Optional[uuid.UUID] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        operator_id: uuid.UUID,
        name: str,
        phone: str,
        licence_number: Optional[str] = None,
        linked_user_id: Optional[uuid.UUID] = None,
    ) -> "Driver":
        if not name.strip():
            raise DomainError("Driver name cannot be empty")
        if not phone.strip():
            raise DomainError("Driver phone cannot be empty")
        return cls(
            id=uuid.uuid4(),
            operator_id=operator_id,
            name=name.strip(),
            phone=phone.strip(),
            licence_number=licence_number,
            linked_user_id=linked_user_id,
        )


@dataclass
class User:
    id: uuid.UUID
    name: str
    is_active: bool = True
    is_admin: bool = False
    # Passenger identity — set for OTP users
    phone: Optional[str] = None
    # Operator/Admin identity — set for password users
    email: Optional[str] = None
    hashed_password: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    # ------------------------------------------------------------------ #
    # Factories — two clear creation paths                                 #
    # ------------------------------------------------------------------ #

    @classmethod
    def create_passenger(cls, phone: str) -> "User":
        """Auto-created on first OTP verification. No password."""
        return cls(
            id=uuid.uuid4(),
            phone=phone,
            name=phone,         # placeholder until they update profile
            email=None,
            hashed_password=None,
        )

    @classmethod
    def create_operator(cls, email: str, hashed_password: str, name: str) -> "User":
        """Created by admin. Password-based login only."""
        return cls(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hashed_password,
            name=name,
            phone=None,
        )

    @classmethod
    def create_admin(cls, email: str, hashed_password: str, name: str) -> "User":
        return cls(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hashed_password,
            name=name,
            phone=None,
            is_admin=True,
        )

    # ------------------------------------------------------------------ #
    # Guards — enforce which login path each user type can use            #
    # ------------------------------------------------------------------ #

    @property
    def is_password_user(self) -> bool:
        """True for operators and admins — they have email+password."""
        return self.email is not None and self.hashed_password is not None

    @property
    def is_phone_user(self) -> bool:
        """True for passengers — they have phone only."""
        return self.phone is not None and self.email is None

    def suspend(self) -> None:
        self.is_active = False

    def unsuspend(self) -> None:
        self.is_active = True