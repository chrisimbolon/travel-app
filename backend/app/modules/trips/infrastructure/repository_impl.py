from datetime import datetime
from typing import Optional
from uuid import UUID

from app.modules.trips.domain.entities import Route, Trip, TripStatus
from app.modules.trips.domain.repositories import (RouteRepository,
                                                   TripRepository)
from sqlalchemy.orm import Session

from .models import RouteModel, TripModel


class SQLTripRepository(TripRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, trip: Trip) -> Trip:
        model = TripModel(
            id=trip.id,
            route_id=trip.route_id,
            operator_id=trip.operator_id,
            driver_id=trip.driver_id,
            departure_at=trip.departure_at,
            total_seats=trip.total_seats,
            available_seats=trip.available_seats,
            price_per_seat=trip.price_per_seat,
            status=trip.status.value,
            booking_code=trip.booking_code,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        model = self.db.query(TripModel).filter(TripModel.id == trip_id).first()
        return self._to_domain(model) if model else None

    def get_by_booking_code(self, code: str) -> Optional[Trip]:
        model = self.db.query(TripModel).filter(TripModel.booking_code == code).first()
        return self._to_domain(model) if model else None

    def list_by_route(
        self,
        route_id: UUID,
        status: Optional[TripStatus] = None,
        from_dt: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Trip]:
        q = self.db.query(TripModel).filter(TripModel.route_id == route_id)
        if status:
            q = q.filter(TripModel.status == status.value)
        if from_dt:
            q = q.filter(TripModel.departure_at >= from_dt)
        q = q.order_by(TripModel.departure_at.asc())
        return [self._to_domain(m) for m in q.limit(limit).offset(offset).all()]

    def list_by_operator(
        self,
        operator_id: UUID,
        status: Optional[TripStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Trip]:
        q = self.db.query(TripModel).filter(TripModel.operator_id == operator_id)
        if status:
            q = q.filter(TripModel.status == status.value)
        q = q.order_by(TripModel.departure_at.asc())
        return [self._to_domain(m) for m in q.limit(limit).offset(offset).all()]

    def update(self, trip: Trip) -> Trip:
        model = self.db.query(TripModel).filter(TripModel.id == trip.id).first()
        if not model:
            raise ValueError(f"Trip {trip.id} not found for update")
        model.driver_id = trip.driver_id
        model.available_seats = trip.available_seats
        model.status = trip.status.value
        model.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def _to_domain(self, m: TripModel) -> Trip:
        return Trip(
            id=m.id,
            route_id=m.route_id,
            operator_id=m.operator_id,
            driver_id=m.driver_id,
            departure_at=m.departure_at,
            total_seats=m.total_seats,
            available_seats=m.available_seats,
            price_per_seat=m.price_per_seat,
            status=TripStatus(m.status),
            booking_code=m.booking_code,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class SQLRouteRepository(RouteRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, route: Route) -> Route:
        model = RouteModel(
            id=route.id,
            origin=route.origin,
            destination=route.destination,
            distance_km=route.distance_km,
            estimated_duration_minutes=route.estimated_duration_minutes,
            is_active=route.is_active,
            created_at=route.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, route_id: UUID) -> Optional[Route]:
        model = self.db.query(RouteModel).filter(RouteModel.id == route_id).first()
        return self._to_domain(model) if model else None

    def list_active(self, limit: int = 50, offset: int = 0) -> list[Route]:
        models = (
            self.db.query(RouteModel)
            .filter(RouteModel.is_active == True)
            .order_by(RouteModel.origin.asc())
            .limit(limit).offset(offset).all()
        )
        return [self._to_domain(m) for m in models]

    def find_by_origin_destination(self, origin: str, destination: str) -> Optional[Route]:
        model = (
            self.db.query(RouteModel)
            .filter(
                RouteModel.origin.ilike(origin.strip()),
                RouteModel.destination.ilike(destination.strip()),
            )
            .first()
        )
        return self._to_domain(model) if model else None

    def _to_domain(self, m: RouteModel) -> Route:
        return Route(
            id=m.id,
            origin=m.origin,
            destination=m.destination,
            distance_km=m.distance_km,
            estimated_duration_minutes=m.estimated_duration_minutes,
            is_active=m.is_active,
            created_at=m.created_at,
        )