from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from .entities import Route, Trip, TripStatus


class TripRepository(ABC):

    @abstractmethod
    def save(self, trip: Trip) -> Trip:
        pass

    @abstractmethod
    def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        pass

    @abstractmethod
    def get_by_booking_code(self, code: str) -> Optional[Trip]:
        pass

    @abstractmethod
    def list_by_route(
        self,
        route_id: UUID,
        status: Optional[TripStatus] = None,
        from_dt: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Trip]:
        pass

    @abstractmethod
    def list_by_operator(
        self,
        operator_id: UUID,
        status: Optional[TripStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Trip]:
        pass

    @abstractmethod
    def update(self, trip: Trip) -> Trip:
        pass


class RouteRepository(ABC):

    @abstractmethod
    def save(self, route: Route) -> Route:
        pass

    @abstractmethod
    def get_by_id(self, route_id: UUID) -> Optional[Route]:
        pass

    @abstractmethod
    def list_active(self, limit: int = 50, offset: int = 0) -> list[Route]:
        pass

    @abstractmethod
    def find_by_origin_destination(
        self, origin: str, destination: str
    ) -> Optional[Route]:
        pass