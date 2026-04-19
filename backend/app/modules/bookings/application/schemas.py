from datetime import datetime
from typing import Optional
from uuid import UUID

from app.modules.bookings.domain.entities import (BookingStatus, PaymentMethod,
                                                  PaymentStatus)
from pydantic import BaseModel, field_validator


class CreateBookingRequest(BaseModel):
    trip_id: UUID
    passenger_name: str
    passenger_phone: str
    seat_numbers: list[int]        # e.g. [3, 7]
    payment_method: PaymentMethod

    @field_validator("seat_numbers")
    @classmethod
    def seats_must_be_valid(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("Must select at least one seat")
        if any(n < 1 for n in v):
            raise ValueError("Seat numbers must be positive integers")
        if len(set(v)) != len(v):
            raise ValueError("Duplicate seat numbers")
        return sorted(v)

    @field_validator("passenger_phone")
    @classmethod
    def phone_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("passenger_phone cannot be empty")
        return v.strip()


class CancelBookingRequest(BaseModel):
    reason: Optional[str] = None


class BookedSeatResponse(BaseModel):
    seat_number: int
    passenger_name: str
    passenger_phone: str


class BookingResponse(BaseModel):
    id: UUID
    trip_id: UUID
    passenger_id: UUID
    passenger_name: str
    passenger_phone: str
    seat_numbers: list[int]
    seat_count: int
    total_price: int
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    status: BookingStatus
    booking_ref: str
    payment_gateway_ref: Optional[str]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentWebhookPayload(BaseModel):
    """
    Normalised webhook shape — works for Midtrans and Xendit.
    In production: verify HMAC signature in middleware before this runs.
    """
    order_id: str            # our payment_gateway_ref
    transaction_status: str  # settlement | capture | pending | deny | expire | cancel
    payment_type: Optional[str] = None
    gross_amount: Optional[str] = None