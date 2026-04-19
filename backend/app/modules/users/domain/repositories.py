from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .entities import Driver, OperatorProfile, OtpCode, User


class UserRepository(ABC):

    @abstractmethod
    async def get_by_phone(self, phone: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def get_or_create_by_phone(self, phone: str) -> tuple[User, bool]:
        """Returns (user, created). Passenger path only."""
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass


class OtpRepository(ABC):

    @abstractmethod
    async def store(self, otp: OtpCode) -> None:
        pass

    @abstractmethod
    async def get(self, phone: str) -> Optional[OtpCode]:
        pass

    @abstractmethod
    async def delete(self, phone: str) -> None:
        pass


class OperatorProfileRepository(ABC):

    @abstractmethod
    async def save(self, profile: OperatorProfile) -> OperatorProfile:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[OperatorProfile]:
        pass

    @abstractmethod
    async def get_by_id(self, profile_id: UUID) -> Optional[OperatorProfile]:
        pass

    @abstractmethod
    async def list_pending(self, limit: int = 50, offset: int = 0) -> list[OperatorProfile]:
        pass

    @abstractmethod
    async def update(self, profile: OperatorProfile) -> OperatorProfile:
        pass


class DriverRepository(ABC):

    @abstractmethod
    async def save(self, driver: Driver) -> Driver:
        pass

    @abstractmethod
    async def get_by_id(self, driver_id: UUID) -> Optional[Driver]:
        pass

    @abstractmethod
    async def list_by_operator(self, operator_id: UUID) -> list[Driver]:
        pass

    @abstractmethod
    async def update(self, driver: Driver) -> Driver:
        pass