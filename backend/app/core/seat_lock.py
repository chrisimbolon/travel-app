import json
from typing import Optional
from uuid import UUID

import redis.asyncio as aioredis

SEAT_LOCK_TTL = 30 * 60  # 30 minutes


def _key(trip_id: UUID, seat_number: int) -> str:
    return f"seat_lock:{trip_id}:{seat_number}"


class SeatLockService:
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client

    async def acquire(self, trip_id: UUID, seat_number: int, booking_id: UUID) -> bool:
        key = _key(trip_id, seat_number)
        value = json.dumps({"booking_id": str(booking_id)})
        result = await self.redis.set(key, value, nx=True, ex=SEAT_LOCK_TTL)
        return result is True

    async def acquire_many(
        self, trip_id: UUID, seat_numbers: list[int], booking_id: UUID
    ) -> tuple[bool, Optional[int]]:
        acquired: list[int] = []
        for seat_number in seat_numbers:
            success = await self.acquire(trip_id, seat_number, booking_id)
            if not success:
                await self.release_many(trip_id, acquired)
                return False, seat_number
            acquired.append(seat_number)
        return True, None

    async def release(self, trip_id: UUID, seat_number: int) -> None:
        await self.redis.delete(_key(trip_id, seat_number))

    async def release_many(self, trip_id: UUID, seat_numbers: list[int]) -> None:
        if seat_numbers:
            keys = [_key(trip_id, n) for n in seat_numbers]
            await self.redis.delete(*keys)

    async def is_locked(self, trip_id: UUID, seat_number: int) -> bool:
        return await self.redis.exists(_key(trip_id, seat_number)) == 1