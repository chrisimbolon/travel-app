from contextlib import asynccontextmanager

from app.core.database import Base, engine
from app.modules.admin.api.routes import router as admin_router
from app.modules.auth.api.routes import router as auth_router
from app.modules.bookings.api.routes import router as bookings_router
from app.modules.trips.api.routes import router as trips_router
from app.workers.auto_cancel import start_scheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()
    await engine.dispose()


app = FastAPI(title="Transitku API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(trips_router)
app.include_router(bookings_router)
app.include_router(admin_router)