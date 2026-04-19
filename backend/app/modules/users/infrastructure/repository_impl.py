import json
import uuid as _uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.core.redis_client import get_redis
from app.modules.users.domain.entities import (Driver, OperatorProfile,
                                               OtpCode, User)
from app.modules.users.domain.repositories import (DriverRepository,
                                                   OperatorProfileRepository,
                                                   OtpRepository,
                                                   UserRepository)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import DriverModel, OperatorProfileModel, UserModel


class SQLUserRepository(UserRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_phone(self, phone: str) -> Optional[User]:
        result = await self.db.execute(
            select(UserModel).where(UserModel.phone == phone)
        )
        m = result.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        m = result.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        m = result.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_or_create_by_phone(self, phone: str) -> tuple[User, bool]:
        result = await self.db.execute(
            select(UserModel).where(UserModel.phone == phone)
        )
        m = result.scalar_one_or_none()
        if m:
            return self._to_domain(m), False

        new_model = UserModel(
            id=_uuid.uuid4(),
            phone=phone,
            name=phone,
            email=None,
            hashed_password=None,
        )
        self.db.add(new_model)
        await self.db.flush()
        await self.db.refresh(new_model)
        return self._to_domain(new_model), True

    async def save(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            phone=user.phone,
            email=user.email,
            hashed_password=user.hashed_password,
            name=user.name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
        )
        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_domain(model)

    async def update(self, user: User) -> User:
        result = await self.db.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        m = result.scalar_one_or_none()
        if not m:
            raise ValueError(f"User {user.id} not found")
        m.name = user.name
        m.is_active = user.is_active
        m.is_admin = user.is_admin
        await self.db.flush()
        await self.db.refresh(m)
        return self._to_domain(m)

    def _to_domain(self, m: UserModel) -> User:
        return User(
            id=m.id,
            name=m.name,
            phone=m.phone,
            email=m.email,
            hashed_password=m.hashed_password,
            is_active=m.is_active,
            is_admin=m.is_admin,
            created_at=m.created_at,
        )


class RedisOtpRepository(OtpRepository):

    async def store(self, otp: OtpCode) -> None:
        import math
        redis = await get_redis()
        ttl = math.ceil(
            (otp.expires_at - datetime.utcnow()).total_seconds()
        )
        value = json.dumps({
            "code": otp.code,
            "expires_at": otp.expires_at.isoformat(),
        })
        await redis.setex(f"otp:{otp.phone}", ttl, value)

    async def get(self, phone: str) -> Optional[OtpCode]:
        redis = await get_redis()
        raw = await redis.get(f"otp:{phone}")
        if not raw:
            return None
        data = json.loads(raw)
        return OtpCode(
            phone=phone,
            code=data["code"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )

    async def delete(self, phone: str) -> None:
        redis = await get_redis()
        await redis.delete(f"otp:{phone}")


class SQLOperatorProfileRepository(OperatorProfileRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, profile: OperatorProfile) -> OperatorProfile:
        model = OperatorProfileModel(
            id=profile.id,
            user_id=profile.user_id,
            business_name=profile.business_name,
            phone=profile.phone,
            is_approved=profile.is_approved,
            approved_at=profile.approved_at,
            approved_by_admin_id=profile.approved_by_admin_id,
            created_at=profile.created_at,
        )
        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_domain(model)

    async def get_by_user_id(self, user_id: UUID) -> Optional[OperatorProfile]:
        result = await self.db.execute(
            select(OperatorProfileModel).where(OperatorProfileModel.user_id == user_id)
        )
        m = result.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def get_by_id(self, profile_id: UUID) -> Optional[OperatorProfile]:
        result = await self.db.execute(
            select(OperatorProfileModel).where(OperatorProfileModel.id == profile_id)
        )
        m = result.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def list_pending(self, limit: int = 50, offset: int = 0) -> list[OperatorProfile]:
        result = await self.db.execute(
            select(OperatorProfileModel)
            .where(OperatorProfileModel.is_approved == False)
            .order_by(OperatorProfileModel.created_at.asc())
            .limit(limit).offset(offset)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def update(self, profile: OperatorProfile) -> OperatorProfile:
        result = await self.db.execute(
            select(OperatorProfileModel).where(OperatorProfileModel.id == profile.id)
        )
        m = result.scalar_one_or_none()
        if not m:
            raise ValueError(f"OperatorProfile {profile.id} not found")
        m.is_approved = profile.is_approved
        m.approved_at = profile.approved_at
        m.approved_by_admin_id = profile.approved_by_admin_id
        await self.db.flush()
        await self.db.refresh(m)
        return self._to_domain(m)

    def _to_domain(self, m: OperatorProfileModel) -> OperatorProfile:
        return OperatorProfile(
            id=m.id,
            user_id=m.user_id,
            business_name=m.business_name,
            phone=m.phone,
            is_approved=m.is_approved,
            approved_at=m.approved_at,
            approved_by_admin_id=m.approved_by_admin_id,
            created_at=m.created_at,
        )


class SQLDriverRepository(DriverRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, driver: Driver) -> Driver:
        model = DriverModel(
            id=driver.id,
            operator_id=driver.operator_id,
            name=driver.name,
            phone=driver.phone,
            licence_number=driver.licence_number,
            linked_user_id=driver.linked_user_id,
            is_active=driver.is_active,
            created_at=driver.created_at,
        )
        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, driver_id: UUID) -> Optional[Driver]:
        result = await self.db.execute(
            select(DriverModel).where(DriverModel.id == driver_id)
        )
        m = result.scalar_one_or_none()
        return self._to_domain(m) if m else None

    async def list_by_operator(self, operator_id: UUID) -> list[Driver]:
        result = await self.db.execute(
            select(DriverModel)
            .where(DriverModel.operator_id == operator_id, DriverModel.is_active == True)
            .order_by(DriverModel.name.asc())
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def update(self, driver: Driver) -> Driver:
        result = await self.db.execute(
            select(DriverModel).where(DriverModel.id == driver.id)
        )
        m = result.scalar_one_or_none()
        if not m:
            raise ValueError(f"Driver {driver.id} not found")
        m.name = driver.name
        m.phone = driver.phone
        m.licence_number = driver.licence_number
        m.is_active = driver.is_active
        await self.db.flush()
        await self.db.refresh(m)
        return self._to_domain(m)

    def _to_domain(self, m: DriverModel) -> Driver:
        return Driver(
            id=m.id,
            operator_id=m.operator_id,
            name=m.name,
            phone=m.phone,
            licence_number=m.licence_number,
            linked_user_id=m.linked_user_id,
            is_active=m.is_active,
            created_at=m.created_at,
        )