from datetime import datetime
from typing import Optional
from uuid import UUID

from app.modules.trips.domain.entities import TripStatus
from pydantic import BaseModel, field_validator


class CreateTripRequest(BaseModel):
    route_id: UUID
    departure_at: datetime
    total_seats: int
    price_per_seat: int          # IDR, integer only

    @field_validator("total_seats")
    @classmethod
    def seats_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("total_seats must be at least 1")
        return v

    @field_validator("price_per_seat")
    @classmethod
    def price_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("price_per_seat cannot be negative")
        return v


class AssignDriverRequest(BaseModel):
    driver_id: UUID


class UpdateTripStatusRequest(BaseModel):
    status: TripStatus


class RouteResponse(BaseModel):
    id: UUID
    origin: str
    destination: str
    distance_km: Optional[float]
    estimated_duration_minutes: Optional[int]
    is_active: bool

    model_config = {"from_attributes": True}


class TripResponse(BaseModel):
    id: UUID
    route_id: UUID
    operator_id: UUID
    driver_id: Optional[UUID]
    departure_at: datetime
    total_seats: int
    available_seats: int
    price_per_seat: int
    status: TripStatus
    booking_code: str
    is_bookable: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateRouteRequest(BaseModel):
    origin: str
    destination: str
    distance_km: Optional[float] = None
    estimated_duration_minutes: Optional[int] = None