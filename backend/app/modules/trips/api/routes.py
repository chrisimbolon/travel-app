from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import require_admin, require_auth, require_operator
from app.modules.trips.application.schemas import (AssignDriverRequest,
                                                   CreateRouteRequest,
                                                   CreateTripRequest,
                                                   RouteResponse, TripResponse,
                                                   UpdateTripStatusRequest)
from app.modules.trips.application.use_cases import (AssignDriverUseCase,
                                                     CreateRouteUseCase,
                                                     CreateTripUseCase,
                                                     GetTripUseCase,
                                                     ListRoutesUseCase,
                                                     ListTripsUseCase,
                                                     UpdateTripStatusUseCase)
from app.modules.trips.domain.entities import DomainError, TripStatus
from app.modules.trips.infrastructure.repository_impl import (
    SQLRouteRepository, SQLTripRepository)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["trips"])


def get_trip_repo(db: AsyncSession = Depends(get_db)) -> SQLTripRepository:
    return SQLTripRepository(db)


def get_route_repo(db: AsyncSession = Depends(get_db)) -> SQLRouteRepository:
    return SQLRouteRepository(db)


@router.get("/routes", response_model=list[RouteResponse])
async def list_routes(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    route_repo: SQLRouteRepository = Depends(get_route_repo),
    _: dict = Depends(require_auth),
):
    return await ListRoutesUseCase(route_repo).execute(limit=limit, offset=offset)


@router.post("/routes", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
async def create_route(
    data: CreateRouteRequest,
    route_repo: SQLRouteRepository = Depends(get_route_repo),
    _: dict = Depends(require_admin),
):
    try:
        return await CreateRouteUseCase(route_repo).execute(
            origin=data.origin,
            destination=data.destination,
            distance_km=data.distance_km,
            estimated_duration_minutes=data.estimated_duration_minutes,
        )
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/trips", response_model=list[TripResponse])
async def list_trips(
    route_id: Optional[UUID] = Query(default=None),
    operator_id: Optional[UUID] = Query(default=None),
    trip_status: Optional[TripStatus] = Query(default=None, alias="status"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    trip_repo: SQLTripRepository = Depends(get_trip_repo),
    _: dict = Depends(require_auth),
):
    try:
        trips = await ListTripsUseCase(trip_repo).execute(
            route_id=route_id,
            operator_id=operator_id,
            status=trip_status,
            limit=limit,
            offset=offset,
        )
        return [_trip_to_response(t) for t in trips]
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    data: CreateTripRequest,
    trip_repo: SQLTripRepository = Depends(get_trip_repo),
    route_repo: SQLRouteRepository = Depends(get_route_repo),
    current_user: dict = Depends(require_operator),
):
    try:
        trip = await CreateTripUseCase(trip_repo, route_repo).execute(
            operator_id=UUID(current_user["operator_profile_id"]),
            route_id=data.route_id,
            departure_at=data.departure_at,
            total_seats=data.total_seats,
            price_per_seat=data.price_per_seat,
        )
        return _trip_to_response(trip)
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/trips/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: UUID,
    trip_repo: SQLTripRepository = Depends(get_trip_repo),
    _: dict = Depends(require_auth),
):
    try:
        return _trip_to_response(await GetTripUseCase(trip_repo).execute(trip_id))
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/trips/{trip_id}/status", response_model=TripResponse)
async def update_trip_status(
    trip_id: UUID,
    data: UpdateTripStatusRequest,
    trip_repo: SQLTripRepository = Depends(get_trip_repo),
    current_user: dict = Depends(require_operator),
):
    try:
        trip = await UpdateTripStatusUseCase(trip_repo).execute(
            trip_id=trip_id,
            new_status=data.status,
            operator_id=UUID(current_user["operator_profile_id"]),
        )
        return _trip_to_response(trip)
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.patch("/trips/{trip_id}/driver", response_model=TripResponse)
async def assign_driver(
    trip_id: UUID,
    data: AssignDriverRequest,
    trip_repo: SQLTripRepository = Depends(get_trip_repo),
    current_user: dict = Depends(require_operator),
):
    try:
        trip = await AssignDriverUseCase(trip_repo).execute(
            trip_id=trip_id,
            driver_id=data.driver_id,
            operator_id=UUID(current_user["operator_profile_id"]),
        )
        return _trip_to_response(trip)
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


def _trip_to_response(trip) -> TripResponse:
    return TripResponse(
        id=trip.id,
        route_id=trip.route_id,
        operator_id=trip.operator_id,
        driver_id=trip.driver_id,
        departure_at=trip.departure_at,
        total_seats=trip.total_seats,
        available_seats=trip.available_seats,
        price_per_seat=trip.price_per_seat,
        status=trip.status,
        booking_code=trip.booking_code,
        is_bookable=trip.is_bookable,
        created_at=trip.created_at,
    )