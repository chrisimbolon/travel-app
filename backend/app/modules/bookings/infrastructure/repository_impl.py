from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.modules.bookings.domain.entities import (BookedSeat, Booking,
                                                  BookingStatus, PaymentMethod,
                                                  PaymentStatus)
from app.modules.bookings.domain.repositories import BookingRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import BookedSeatModel, BookingModel


class SQLBookingRepository(BookingRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, booking: Booking, seats: list[BookedSeat]) -> Booking:
        model = BookingModel(
            id=booking.id,
            trip_id=booking.trip_id,
            passenger_id=booking.passenger_id,
            passenger_name=booking.passenger_name,
            passenger_phone=booking.passenger_phone,
            seat_numbers=booking.seat_numbers,
            seat_count=booking.seat_count,
            total_price=booking.total_price,
            payment_method=booking.payment_method.value,
            payment_status=booking.payment_status.value,
            status=booking.status.value,
            booking_ref=booking.booking_ref,
            payment_gateway_ref=booking.payment_gateway_ref,
            cancelled_at=booking.cancelled_at,
            cancellation_reason=booking.cancellation_reason,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )
        self.db.add(model)

        for seat in seats:
            self.db.add(BookedSeatModel(
                id=seat.id,
                booking_id=seat.booking_id,
                trip_id=seat.trip_id,
                seat_number=seat.seat_number,
                passenger_name=seat.passenger_name,
                passenger_phone=seat.passenger_phone,
            ))

        await self.db.flush()
        await self.db.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, booking_id: UUID) -> Optional[Booking]:
        result = await self.db.execute(
            select(BookingModel).where(BookingModel.id == booking_id)
        )
        m = result.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_ref(self, booking_ref: str) -> Optional[Booking]:
        result = await self.db.execute(
            select(BookingModel).where(BookingModel.booking_ref == booking_ref)
        )
        m = result.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_gateway_ref(self, gateway_ref: str) -> Optional[Booking]:
        result = await self.db.execute(
            select(BookingModel).where(BookingModel.payment_gateway_ref == gateway_ref)
        )
        m = result.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def list_by_passenger(
        self,
        passenger_id: UUID,
        status: Optional[BookingStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Booking]:
        q = select(BookingModel).where(BookingModel.passenger_id == passenger_id)
        if status:
            q = q.where(BookingModel.status == status.value)
        q = q.order_by(BookingModel.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(q)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def list_by_trip(
        self,
        trip_id: UUID,
        status: Optional[BookingStatus] = None,
    ) -> list[Booking]:
        q = select(BookingModel).where(BookingModel.trip_id == trip_id)
        if status:
            q = q.where(BookingModel.status == status.value)
        q = q.order_by(BookingModel.created_at.asc())
        result = await self.db.execute(q)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def list_pending_expired(self, older_than_minutes: int) -> list[Booking]:
        cutoff = datetime.utcnow() - timedelta(minutes=older_than_minutes)
        result = await self.db.execute(
            select(BookingModel).where(
                BookingModel.status == BookingStatus.PENDING.value,
                BookingModel.created_at <= cutoff,
            )
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_booked_seat_numbers(self, trip_id: UUID) -> set[int]:
        result = await self.db.execute(
            select(BookedSeatModel.seat_number)
            .join(BookingModel, BookedSeatModel.booking_id == BookingModel.id)
            .where(
                BookedSeatModel.trip_id == trip_id,
                BookingModel.status.in_([
                    BookingStatus.PENDING.value,
                    BookingStatus.CONFIRMED.value,
                    BookingStatus.BOARDED.value,
                ]),
            )
        )
        return {row.seat_number for row in result.all()}

    async def update(self, booking: Booking) -> Booking:
        result = await self.db.execute(
            select(BookingModel).where(BookingModel.id == booking.id)
        )
        m = result.scalar_one_or_none()
        if not m:
            raise ValueError(f"Booking {booking.id} not found for update")
        m.status = booking.status.value
        m.payment_status = booking.payment_status.value
        m.payment_gateway_ref = booking.payment_gateway_ref
        m.cancelled_at = booking.cancelled_at
        m.cancellation_reason = booking.cancellation_reason
        m.updated_at = booking.updated_at
        await self.db.flush()
        await self.db.refresh(m)
        return self._to_domain(m)

    async def delete_seats(self, booking_id: UUID) -> None:
        result = await self.db.execute(
            select(BookedSeatModel).where(BookedSeatModel.booking_id == booking_id)
        )
        for row in result.scalars().all():
            await self.db.delete(row)
        await self.db.flush()

    def _to_domain(self, m: BookingModel) -> Booking:
        return Booking(
            id=m.id,
            trip_id=m.trip_id,
            passenger_id=m.passenger_id,
            passenger_name=m.passenger_name,
            passenger_phone=m.passenger_phone,
            seat_numbers=list(m.seat_numbers),
            seat_count=m.seat_count,
            total_price=m.total_price,
            payment_method=PaymentMethod(m.payment_method),
            payment_status=PaymentStatus(m.payment_status),
            status=BookingStatus(m.status),
            booking_ref=m.booking_ref,
            payment_gateway_ref=m.payment_gateway_ref,
            cancelled_at=m.cancelled_at,
            cancellation_reason=m.cancellation_reason,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )