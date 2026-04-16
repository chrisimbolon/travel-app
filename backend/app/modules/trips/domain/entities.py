import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TripStatus(str, Enum):
    SCHEDULED = "scheduled"
    BOARDING = "boarding"
    DEPARTED = "departed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DomainError(Exception):
    """Raised when a business rule is violated."""


# Valid transitions — domain rule, not a DB concern
_ALLOWED_TRANSITIONS: dict[TripStatus, set[TripStatus]] = {
    TripStatus.SCHEDULED: {TripStatus.BOARDING, TripStatus.CANCELLED},
    TripStatus.BOARDING:  {TripStatus.DEPARTED, TripStatus.CANCELLED},
    TripStatus.DEPARTED:  {TripStatus.COMPLETED},
    TripStatus.COMPLETED: set(),
    TripStatus.CANCELLED: set(),
}


@dataclass
class Route:
    id: uuid.UUID
    origin: str
    destination: str
    distance_km: Optional[float]
    estimated_duration_minutes: Optional[int]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        origin: str,
        destination: str,
        distance_km: Optional[float] = None,
        estimated_duration_minutes: Optional[int] = None,
    ) -> "Route":
        if not origin.strip() or not destination.strip():
            raise DomainError("Origin and destination cannot be empty")
        if origin.strip().lower() == destination.strip().lower():
            raise DomainError("Origin and destination cannot be the same")
        return cls(
            id=uuid.uuid4(),
            origin=origin.strip(),
            destination=destination.strip(),
            distance_km=distance_km,
            estimated_duration_minutes=estimated_duration_minutes,
        )


@dataclass
class Trip:
    id: uuid.UUID
    route_id: uuid.UUID
    operator_id: uuid.UUID
    departure_at: datetime
    total_seats: int
    available_seats: int
    price_per_seat: int          # stored in IDR (integer, no float money bugs)
    status: TripStatus
    booking_code: str
    driver_id: Optional[uuid.UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # ------------------------------------------------------------------ #
    # Factory                                                              #
    # ------------------------------------------------------------------ #
    @classmethod
    def create(
        cls,
        route_id: uuid.UUID,
        operator_id: uuid.UUID,
        departure_at: datetime,
        total_seats: int,
        price_per_seat: int,
        driver_id: Optional[uuid.UUID] = None,
    ) -> "Trip":
        if total_seats < 1:
            raise DomainError("A trip must have at least one seat")
        if price_per_seat < 0:
            raise DomainError("Price cannot be negative")
        if departure_at <= datetime.utcnow():
            raise DomainError("Departure time must be in the future")

        return cls(
            id=uuid.uuid4(),
            route_id=route_id,
            operator_id=operator_id,
            driver_id=driver_id,
            departure_at=departure_at,
            total_seats=total_seats,
            available_seats=total_seats,
            price_per_seat=price_per_seat,
            status=TripStatus.SCHEDULED,
            booking_code=cls._generate_booking_code(),
        )

    # ------------------------------------------------------------------ #
    # State transitions — only valid paths allowed                        #
    # ------------------------------------------------------------------ #
    def _transition_to(self, new_status: TripStatus) -> None:
        allowed = _ALLOWED_TRANSITIONS[self.status]
        if new_status not in allowed:
            raise DomainError(
                f"Cannot transition trip from '{self.status}' to '{new_status}'. "
                f"Allowed: {[s.value for s in allowed] or 'none'}"
            )
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def start_boarding(self) -> None:
        self._transition_to(TripStatus.BOARDING)

    def depart(self) -> None:
        self._transition_to(TripStatus.DEPARTED)

    def complete(self) -> None:
        self._transition_to(TripStatus.COMPLETED)

    def cancel(self) -> None:
        self._transition_to(TripStatus.CANCELLED)

    # ------------------------------------------------------------------ #
    # Seat management                                                      #
    # ------------------------------------------------------------------ #
    def reserve_seats(self, count: int) -> None:
        """Called by booking module when seats are locked."""
        if count < 1:
            raise DomainError("Must reserve at least one seat")
        if count > self.available_seats:
            raise DomainError(
                f"Not enough seats. Requested {count}, available {self.available_seats}"
            )
        self.available_seats -= count
        self.updated_at = datetime.utcnow()

    def release_seats(self, count: int) -> None:
        """Called when a booking is cancelled."""
        if count < 1:
            raise DomainError("Must release at least one seat")
        self.available_seats = min(self.total_seats, self.available_seats + count)
        self.updated_at = datetime.utcnow()

    @property
    def is_bookable(self) -> bool:
        return (
            self.status == TripStatus.SCHEDULED
            and self.available_seats > 0
            and self.departure_at > datetime.utcnow()
        )

    @staticmethod
    def _generate_booking_code() -> str:
        import random
        import string
        return "TRK-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))