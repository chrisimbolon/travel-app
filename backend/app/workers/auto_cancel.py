import asyncio
import logging

from app.core.database import AsyncSessionLocal
from app.core.redis_client import get_redis
from app.core.seat_lock import SeatLockService
from app.modules.bookings.application.use_cases import \
    AutoCancelExpiredBookingsUseCase
from app.modules.bookings.infrastructure.repository_impl import \
    SQLBookingRepository
from app.modules.trips.infrastructure.repository_impl import SQLTripRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)


async def run_auto_cancel() -> None:
    async with AsyncSessionLocal() as db:
        try:
            redis = await get_redis()
            cancelled = await AutoCancelExpiredBookingsUseCase(
                booking_repo=SQLBookingRepository(db),
                trip_repo=SQLTripRepository(db),
                seat_lock=SeatLockService(redis),
            ).execute()
            if cancelled:
                logger.info(f"Auto-cancel: cancelled {cancelled} expired bookings")
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Auto-cancel error: {e}", exc_info=True)


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_auto_cancel, "interval", minutes=5, id="auto_cancel_bookings"
    )
    scheduler.start()
    logger.info("Auto-cancel scheduler started")
    return scheduler