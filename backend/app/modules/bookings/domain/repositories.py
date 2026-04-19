from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .entities import BookedSeat, Booking, BookingStatus


class BookingRepository(ABC):

    @abstractmethod
    def save(self, booking: Booking, seats: list[BookedSeat]) -> Booking:
        """Save booking + its BookedSeat rows atomically."""
        pass

    @abstractmethod
    def get_by_id(self, booking_id: UUID) -> Optional[Booking]:
        pass

    @abstractmethod
    def get_by_ref(self, booking_ref: str) -> Optional[Booking]:
        pass

    @abstractmethod
    def get_by_gateway_ref(self, gateway_ref: str) -> Optional[Booking]:
        pass

    @abstractmethod
    def list_by_passenger(
        self,
        passenger_id: UUID,
        status: Optional[BookingStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Booking]:
        pass

    @abstractmethod
    def list_by_trip(
        self,
        trip_id: UUID,
        status: Optional[BookingStatus] = None,
    ) -> list[Booking]:
        pass

    @abstractmethod
    def list_pending_expired(self, older_than_minutes: int) -> list[Booking]:
        """Used by auto-cancel worker to find stale pending bookings."""
        pass

    @abstractmethod
    def get_booked_seat_numbers(self, trip_id: UUID) -> set[int]:
        """Returns all seat numbers currently locked on a trip (not cancelled)."""
        pass

    @abstractmethod
    def update(self, booking: Booking) -> Booking:
        pass

    @abstractmethod
    def delete_seats(self, booking_id: UUID) -> None:
        """Remove BookedSeat rows when booking is cancelled."""
        pass