import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class BookingStatus(str, Enum):
    PENDING    = "pending"
    CONFIRMED  = "confirmed"
    BOARDED    = "boarded"
    COMPLETED  = "completed"
    CANCELLED  = "cancelled"


class PaymentMethod(str, Enum):
    CASH          = "cash"
    QRIS          = "qris"
    BANK_TRANSFER = "bank_transfer"
    EWALLET       = "ewallet"


class PaymentStatus(str, Enum):
    UNPAID   = "unpaid"
    PAID     = "paid"
    REFUNDED = "refunded"


class DomainError(Exception):
    """Raised when a booking business rule is violated."""


_ALLOWED_TRANSITIONS: dict[BookingStatus, set[BookingStatus]] = {
    BookingStatus.PENDING:   {BookingStatus.CONFIRMED, BookingStatus.CANCELLED},
    BookingStatus.CONFIRMED: {BookingStatus.BOARDED,   BookingStatus.CANCELLED},
    BookingStatus.BOARDED:   {BookingStatus.COMPLETED},
    BookingStatus.COMPLETED: set(),
    BookingStatus.CANCELLED: set(),
}

# Payment methods that require a gateway and stay pending until webhook
DIGITAL_PAYMENT_METHODS = {
    PaymentMethod.QRIS,
    PaymentMethod.BANK_TRANSFER,
    PaymentMethod.EWALLET,
}


@dataclass
class BookedSeat:
    """One row per seat number. Enables clean manifest and seat conflict detection."""
    id: uuid.UUID
    booking_id: uuid.UUID
    trip_id: uuid.UUID
    seat_number: int
    passenger_name: str
    passenger_phone: str

    @classmethod
    def create(
        cls,
        booking_id: uuid.UUID,
        trip_id: uuid.UUID,
        seat_number: int,
        passenger_name: str,
        passenger_phone: str,
    ) -> "BookedSeat":
        if seat_number < 1:
            raise DomainError(f"Invalid seat number: {seat_number}")
        return cls(
            id=uuid.uuid4(),
            booking_id=booking_id,
            trip_id=trip_id,
            seat_number=seat_number,
            passenger_name=passenger_name.strip(),
            passenger_phone=passenger_phone.strip(),
        )


@dataclass
class Booking:
    id: uuid.UUID
    trip_id: uuid.UUID
    passenger_id: uuid.UUID
    passenger_name: str
    passenger_phone: str
    seat_numbers: list[int]           # e.g. [3, 7]
    seat_count: int                   # len(seat_numbers) — denormalised for queries
    total_price: int                  # IDR integer — seat_count × price_per_seat
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    status: BookingStatus
    booking_ref: str                  # e.g. BK-A1B2C3D4
    payment_gateway_ref: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # ------------------------------------------------------------------ #
    # Factory                                                              #
    # ------------------------------------------------------------------ #
    @classmethod
    def create(
        cls,
        trip_id: uuid.UUID,
        passenger_id: uuid.UUID,
        passenger_name: str,
        passenger_phone: str,
        seat_numbers: list[int],
        price_per_seat: int,
        payment_method: PaymentMethod,
    ) -> "Booking":
        if not seat_numbers:
            raise DomainError("Must select at least one seat")
        if len(set(seat_numbers)) != len(seat_numbers):
            raise DomainError("Duplicate seat numbers in request")
        if not passenger_name.strip():
            raise DomainError("Passenger name cannot be empty")
        if not passenger_phone.strip():
            raise DomainError("Passenger phone cannot be empty")
        if price_per_seat < 0:
            raise DomainError("Price per seat cannot be negative")

        seat_count = len(seat_numbers)
        total_price = seat_count * price_per_seat

        return cls(
            id=uuid.uuid4(),
            trip_id=trip_id,
            passenger_id=passenger_id,
            passenger_name=passenger_name.strip(),
            passenger_phone=passenger_phone.strip(),
            seat_numbers=sorted(seat_numbers),
            seat_count=seat_count,
            total_price=total_price,
            payment_method=payment_method,
            payment_status=PaymentStatus.UNPAID,
            # ALL methods start pending — confirmed via webhook or board scan
            status=BookingStatus.PENDING,
            booking_ref=cls._generate_ref(),
        )

    # ------------------------------------------------------------------ #
    # State transitions                                                    #
    # ------------------------------------------------------------------ #
    def _transition_to(self, new_status: BookingStatus) -> None:
        allowed = _ALLOWED_TRANSITIONS[self.status]
        if new_status not in allowed:
            raise DomainError(
                f"Cannot move booking from '{self.status}' to '{new_status}'. "
                f"Allowed: {[s.value for s in allowed] or 'none'}"
            )
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def confirm(self) -> None:
        """Called on successful payment webhook, or manually for cash."""
        self._transition_to(BookingStatus.CONFIRMED)
        self.payment_status = PaymentStatus.PAID
        self.updated_at = datetime.utcnow()

    def mark_boarded(self) -> None:
        self._transition_to(BookingStatus.BOARDED)

    def mark_completed(self) -> None:
        self._transition_to(BookingStatus.COMPLETED)

    def cancel(self, reason: Optional[str] = None) -> None:
        self._transition_to(BookingStatus.CANCELLED)
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
        self.updated_at = datetime.utcnow()

    @property
    def is_cancellable(self) -> bool:
        return self.status in {BookingStatus.PENDING, BookingStatus.CONFIRMED}

    @property
    def requires_payment_gateway(self) -> bool:
        return self.payment_method in DIGITAL_PAYMENT_METHODS

    @staticmethod
    def _generate_ref() -> str:
        import random
        import string
        return "BK-" + "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )