from app.core.database import Base, engine
from app.modules.auth.api.routes import router as auth_router
from app.modules.users.api.routes import router as users_router
from app.modules.users.infrastructure.models import User
from fastapi import FastAPI

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users_router)
app.include_router(auth_router)