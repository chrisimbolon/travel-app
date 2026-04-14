from app.core.database import Base, engine
from app.modules.users.api.routes import router as users_router
from app.modules.users.infrastructure.models import UserModel
from fastapi import FastAPI

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users_router)