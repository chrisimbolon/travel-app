from contextlib import asynccontextmanager

from app.core.database import Base, engine
from app.modules.auth.api.routes import router as auth_router
from app.modules.trips.api.routes import router as trips_router
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Transitku API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(trips_router)