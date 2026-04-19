from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import require_operator_or_admin, require_passenger
from app.core.redis_client import get_redis
from app.core.seat_lock import SeatLockService
from app.core.security import get_current_user
from app.modules.bookings.application.schemas import (BookingResponse,
                                                      CancelBookingRequest,
                                                      CreateBookingRequest,
                                                      PaymentWebhookPayload)
from app.modules.bookings.application.use_cases import (CancelBookingUseCase,
                                                        ConfirmPaymentUseCase,
                                                        CreateBookingUseCase,
                                                        GetBookingUseCase,
                                                        GetTripManifestUseCase,
                                                        ListMyBookingsUseCase)
from app.modules.bookings.domain.entities import BookingStatus, DomainError
from app.modules.bookings.infrastructure.repository_impl import \
    SQLBookingRepository
from app.modules.trips.infrastructure.repository_impl import SQLTripRepository
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["bookings"])


def get_booking_repo(db: AsyncSession = Depends(get_db)) -> SQLBookingRepository:
    return SQLBookingRepository(db)


def get_trip_repo(db: AsyncSession = Depends(get_db)) -> SQLTripRepository:
    return SQLTripRepository(db)


async def get_seat_lock() -> SeatLockService:
    return SeatLockService(await get_redis())


@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: CreateBookingRequest,
    booking_repo: SQLBookingRepository = Depends(get_booking_repo),
    trip_repo: SQLTripRepository = Depends(get_trip_repo),
    seat_lock: SeatLockService = Depends(get_seat_lock),
    current_user: dict = Depends(require_passenger),
):
    try:
        booking = await CreateBookingUseCase(booking_repo, trip_repo, seat_lock).execute(
            trip_id=data.trip_id,
            passenger_id=UUID(current_user["user_id"]),
            passenger_name=data.passenger_name,
            passenger_phone=data.passenger_phone,
            seat_numbers=data.seat_numbers,
            payment_method=data.payment_method,
        )
        return _to_response(booking)
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/bookings", response_model=list[BookingResponse])
async def list_my_bookings(
    booking_status: Optional[BookingStatus] = Query(default=None, alias="status"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    booking_repo: SQLBookingRepository = Depends(get_booking_repo),
    current_user: dict = Depends(require_passenger),
):
    bookings = await ListMyBookingsUseCase(booking_repo).execute(
        passenger_id=UUID(current_user["user_id"]),
        status=booking_status,
        limit=limit,
        offset=offset,
    )
    return [_to_response(b) for b in bookings]


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    booking_repo: SQLBookingRepository = Depends(get_booking_repo),
    current_user: dict = Depends(require_passenger),
):
    try:
        return _to_response(
            await GetBookingUseCase(booking_repo).execute(
                booking_id=booking_id,
                passenger_id=UUID(current_user["user_id"]),
            )
        )
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/bookings/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    data: CancelBookingRequest,
    booking_repo: SQLBookingRepository = Depends(get_booking_repo),
    trip_repo: SQLTripRepository = Depends(get_trip_repo),
    seat_lock: SeatLockService = Depends(get_seat_lock),
    current_user: dict = Depends(require_passenger),
):
    try:
        return _to_response(
            await CancelBookingUseCase(booking_repo, trip_repo, seat_lock).execute(
                booking_id=booking_id,
                passenger_id=UUID(current_user["user_id"]),
                reason=data.reason,
            )
        )
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/trips/{trip_id}/manifest", response_model=list[BookingResponse])
async def get_trip_manifest(
    trip_id: UUID,
    booking_repo: SQLBookingRepository = Depends(get_booking_repo),
    trip_repo: SQLTripRepository = Depends(get_trip_repo),
    current_user: dict = Depends(require_operator_or_admin),
):
    try:
        bookings = await GetTripManifestUseCase(booking_repo, trip_repo).execute(
            trip_id=trip_id,
            operator_id=UUID(current_user["operator_profile_id"]),
        )
        return [_to_response(b) for b in bookings]
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/webhooks/payment", status_code=status.HTTP_200_OK)
async def payment_webhook(
    payload: PaymentWebhookPayload,
    booking_repo: SQLBookingRepository = Depends(get_booking_repo),
):
    try:
        await ConfirmPaymentUseCase(booking_repo).execute(
            gateway_ref=payload.order_id,
            transaction_status=payload.transaction_status,
        )
    except DomainError:
        pass
    return {"status": "ok"}


def _to_response(booking) -> BookingResponse:
    return BookingResponse(
        id=booking.id,
        trip_id=booking.trip_id,
        passenger_id=booking.passenger_id,
        passenger_name=booking.passenger_name,
        passenger_phone=booking.passenger_phone,
        seat_numbers=booking.seat_numbers,
        seat_count=booking.seat_count,
        total_price=booking.total_price,
        payment_method=booking.payment_method,
        payment_status=booking.payment_status,
        status=booking.status,
        booking_ref=booking.booking_ref,
        payment_gateway_ref=booking.payment_gateway_ref,
        cancelled_at=booking.cancelled_at,
        cancellation_reason=booking.cancellation_reason,
        created_at=booking.created_at,
    )