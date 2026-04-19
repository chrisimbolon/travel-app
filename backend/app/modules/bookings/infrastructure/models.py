import uuid
from datetime import datetime

from app.core.database import Base
from sqlalchemy import (BigInteger, DateTime, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class BookingModel(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    passenger_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    passenger_name: Mapped[str] = mapped_column(String(150), nullable=False)
    passenger_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    seat_numbers: Mapped[list] = mapped_column(ARRAY(Integer), nullable=False)
    seat_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="unpaid")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    booking_ref: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    payment_gateway_ref: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seats: Mapped[list["BookedSeatModel"]] = relationship(
        "BookedSeatModel", back_populates="booking", cascade="all, delete-orphan"
    )


class BookedSeatModel(Base):
    __tablename__ = "booked_seats"
    __table_args__ = (
        # One seat per trip — prevents double booking at DB level as a safety net
        UniqueConstraint("trip_id", "seat_number", name="uq_trip_seat"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    seat_number: Mapped[int] = mapped_column(Integer, nullable=False)
    passenger_name: Mapped[str] = mapped_column(String(150), nullable=False)
    passenger_phone: Mapped[str] = mapped_column(String(20), nullable=False)

    booking: Mapped["BookingModel"] = relationship("BookingModel", back_populates="seats")