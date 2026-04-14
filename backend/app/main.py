from app.modules.users.api.routes import router as users_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(users_router)