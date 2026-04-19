from datetime import datetime, timedelta
from uuid import UUID

from app.core.seat_lock import SeatLockService
from app.modules.bookings.domain.entities import (BookedSeat, Booking,
                                                  BookingStatus, DomainError,
                                                  PaymentMethod)
from app.modules.bookings.domain.repositories import BookingRepository
from app.modules.trips.domain.repositories import TripRepository

BOOKING_EXPIRY_MINUTES = 30


class CreateBookingUseCase:
    def __init__(
        self,
        booking_repo: BookingRepository,
        trip_repo: TripRepository,
        seat_lock: SeatLockService,
    ):
        self.booking_repo = booking_repo
        self.trip_repo = trip_repo
        self.seat_lock = seat_lock

    async def execute(
        self,
        trip_id: UUID,
        passenger_id: UUID,
        passenger_name: str,
        passenger_phone: str,
        seat_numbers: list[int],
        payment_method: PaymentMethod,
    ) -> Booking:
        trip = await self.trip_repo.get_by_id(trip_id)
        if not trip:
            raise DomainError(f"Trip {trip_id} not found")
        if not trip.is_bookable:
            raise DomainError(
                "This trip is not available for booking — "
                "it may have departed, been cancelled, or have no seats left."
            )

        for seat_number in seat_numbers:
            if seat_number > trip.total_seats:
                raise DomainError(
                    f"Seat {seat_number} does not exist "
                    f"(max seat: {trip.total_seats})"
                )

        booked = await self.booking_repo.get_booked_seat_numbers(trip_id)
        conflicts = set(seat_numbers) & booked
        if conflicts:
            raise DomainError(f"Seat(s) {sorted(conflicts)} are already booked")

        import uuid as _uuid
        temp_id = _uuid.uuid4()
        success, conflict_seat = await self.seat_lock.acquire_many(
            trip_id, seat_numbers, temp_id
        )
        if not success:
            raise DomainError(
                f"Seat {conflict_seat} was just taken. Please select a different seat."
            )

        try:
            booking = Booking.create(
                trip_id=trip_id,
                passenger_id=passenger_id,
                passenger_name=passenger_name,
                passenger_phone=passenger_phone,
                seat_numbers=seat_numbers,
                price_per_seat=trip.price_per_seat,
                payment_method=payment_method,
            )

            booked_seat_entities = [
                BookedSeat.create(
                    booking_id=booking.id,
                    trip_id=trip_id,
                    seat_number=n,
                    passenger_name=passenger_name,
                    passenger_phone=passenger_phone,
                )
                for n in seat_numbers
            ]

            trip.reserve_seats(len(seat_numbers))
            await self.trip_repo.update(trip)
            return await self.booking_repo.save(booking, booked_seat_entities)

        except Exception:
            await self.seat_lock.release_many(trip_id, seat_numbers)
            raise


class GetBookingUseCase:
    def __init__(self, repo: BookingRepository):
        self.repo = repo

    async def execute(self, booking_id: UUID, passenger_id: UUID) -> Booking:
        booking = await self.repo.get_by_id(booking_id)
        if not booking:
            raise DomainError(f"Booking {booking_id} not found")
        if booking.passenger_id != passenger_id:
            raise DomainError("You do not own this booking")
        return booking


class ListMyBookingsUseCase:
    def __init__(self, repo: BookingRepository):
        self.repo = repo

    async def execute(
        self,
        passenger_id: UUID,
        status: BookingStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Booking]:
        return await self.repo.list_by_passenger(
            passenger_id, status=status, limit=limit, offset=offset
        )


class CancelBookingUseCase:
    def __init__(
        self,
        booking_repo: BookingRepository,
        trip_repo: TripRepository,
        seat_lock: SeatLockService,
    ):
        self.booking_repo = booking_repo
        self.trip_repo = trip_repo
        self.seat_lock = seat_lock

    async def execute(
        self,
        booking_id: UUID,
        passenger_id: UUID | None,
        reason: str | None = None,
    ) -> Booking:
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise DomainError(f"Booking {booking_id} not found")
        if passenger_id and booking.passenger_id != passenger_id:
            raise DomainError("You do not own this booking")
        if not booking.is_cancellable:
            raise DomainError(
                f"Booking cannot be cancelled at status '{booking.status}'"
            )

        trip = await self.trip_repo.get_by_id(booking.trip_id)
        if trip:
            trip.release_seats(booking.seat_count)
            await self.trip_repo.update(trip)

        booking.cancel(reason=reason)
        await self.booking_repo.delete_seats(booking.id)
        await self.seat_lock.release_many(booking.trip_id, booking.seat_numbers)
        return await self.booking_repo.update(booking)


class ConfirmPaymentUseCase:
    def __init__(self, repo: BookingRepository):
        self.repo = repo

    async def execute(self, gateway_ref: str, transaction_status: str) -> Booking | None:
        booking = await self.repo.get_by_gateway_ref(gateway_ref)
        if not booking:
            raise DomainError(f"No booking for gateway ref '{gateway_ref}'")
        if transaction_status in {"settlement", "capture"}:
            if booking.status == BookingStatus.PENDING:
                booking.confirm()
                return await self.repo.update(booking)
        return booking


class AutoCancelExpiredBookingsUseCase:
    def __init__(
        self,
        booking_repo: BookingRepository,
        trip_repo: TripRepository,
        seat_lock: SeatLockService,
    ):
        self.booking_repo = booking_repo
        self.trip_repo = trip_repo
        self.seat_lock = seat_lock

    async def execute(self) -> int:
        expired = await self.booking_repo.list_pending_expired(
            older_than_minutes=BOOKING_EXPIRY_MINUTES
        )
        cancelled = 0
        for booking in expired:
            try:
                await CancelBookingUseCase(
                    self.booking_repo, self.trip_repo, self.seat_lock
                ).execute(
                    booking_id=booking.id,
                    passenger_id=None,
                    reason="Auto-cancelled: payment not completed within 30 minutes",
                )
                cancelled += 1
            except DomainError:
                continue
        return cancelled


class GetTripManifestUseCase:
    def __init__(self, booking_repo: BookingRepository, trip_repo: TripRepository):
        self.booking_repo = booking_repo
        self.trip_repo = trip_repo

    async def execute(self, trip_id: UUID, operator_id: UUID) -> list[Booking]:
        trip = await self.trip_repo.get_by_id(trip_id)
        if not trip:
            raise DomainError(f"Trip {trip_id} not found")
        if trip.operator_id != operator_id:
            raise DomainError("You do not own this trip")
        return await self.booking_repo.list_by_trip(
            trip_id, status=BookingStatus.CONFIRMED
        )