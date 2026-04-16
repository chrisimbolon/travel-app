from datetime import datetime
from typing import Optional
from uuid import UUID

from app.modules.trips.domain.entities import (DomainError, Route, Trip,
                                               TripStatus)
from app.modules.trips.domain.repositories import (RouteRepository,
                                                   TripRepository)


class CreateRouteUseCase:
    def __init__(self, repo: RouteRepository):
        self.repo = repo

    def execute(
        self,
        origin: str,
        destination: str,
        distance_km: Optional[float],
        estimated_duration_minutes: Optional[int],
    ) -> Route:
        existing = self.repo.find_by_origin_destination(origin, destination)
        if existing:
            raise DomainError(f"Route {origin} → {destination} already exists")
        route = Route.create(origin, destination, distance_km, estimated_duration_minutes)
        return self.repo.save(route)


class ListRoutesUseCase:
    def __init__(self, repo: RouteRepository):
        self.repo = repo

    def execute(self, limit: int = 50, offset: int = 0) -> list[Route]:
        return self.repo.list_active(limit=limit, offset=offset)


class CreateTripUseCase:
    def __init__(self, trip_repo: TripRepository, route_repo: RouteRepository):
        self.trip_repo = trip_repo
        self.route_repo = route_repo

    def execute(
        self,
        operator_id: UUID,
        route_id: UUID,
        departure_at: datetime,
        total_seats: int,
        price_per_seat: int,
        driver_id: Optional[UUID] = None,
    ) -> Trip:
        route = self.route_repo.get_by_id(route_id)
        if not route:
            raise DomainError(f"Route {route_id} not found")
        if not route.is_active:
            raise DomainError("Cannot create a trip on an inactive route")

        trip = Trip.create(
            route_id=route_id,
            operator_id=operator_id,
            departure_at=departure_at,
            total_seats=total_seats,
            price_per_seat=price_per_seat,
            driver_id=driver_id,
        )
        return self.trip_repo.save(trip)


class GetTripUseCase:
    def __init__(self, repo: TripRepository):
        self.repo = repo

    def execute(self, trip_id: UUID) -> Trip:
        trip = self.repo.get_by_id(trip_id)
        if not trip:
            raise DomainError(f"Trip {trip_id} not found")
        return trip


class ListTripsUseCase:
    def __init__(self, repo: TripRepository):
        self.repo = repo

    def execute(
        self,
        route_id: Optional[UUID] = None,
        operator_id: Optional[UUID] = None,
        status: Optional[TripStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Trip]:
        if route_id:
            return self.repo.list_by_route(route_id, status=status, limit=limit, offset=offset)
        if operator_id:
            return self.repo.list_by_operator(operator_id, status=status, limit=limit, offset=offset)
        raise DomainError("Must filter by route_id or operator_id")


class UpdateTripStatusUseCase:
    """
    Single use case for all status transitions.
    The domain entity enforces which transitions are valid.
    """
    def __init__(self, repo: TripRepository):
        self.repo = repo

    def execute(self, trip_id: UUID, new_status: TripStatus, operator_id: UUID) -> Trip:
        trip = self.repo.get_by_id(trip_id)
        if not trip:
            raise DomainError(f"Trip {trip_id} not found")
        if trip.operator_id != operator_id:
            raise DomainError("You do not own this trip")

        # let the domain entity enforce the valid transition
        match new_status:
            case TripStatus.BOARDING:
                trip.start_boarding()
            case TripStatus.DEPARTED:
                trip.depart()
            case TripStatus.COMPLETED:
                trip.complete()
            case TripStatus.CANCELLED:
                trip.cancel()
            case _:
                raise DomainError(f"Cannot manually set status to '{new_status}'")

        return self.repo.update(trip)


class AssignDriverUseCase:
    def __init__(self, repo: TripRepository):
        self.repo = repo

    def execute(self, trip_id: UUID, driver_id: UUID, operator_id: UUID) -> Trip:
        trip = self.repo.get_by_id(trip_id)
        if not trip:
            raise DomainError(f"Trip {trip_id} not found")
        if trip.operator_id != operator_id:
            raise DomainError("You do not own this trip")
        if trip.status not in {TripStatus.SCHEDULED, TripStatus.BOARDING}:
            raise DomainError("Cannot assign driver to a trip that has already departed")
        trip.driver_id = driver_id
        return self.repo.update(trip)