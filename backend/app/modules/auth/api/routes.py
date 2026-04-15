# modules/auth/api/routes.py
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.application.schemas import RegisterRequest
from app.modules.auth.application.use_cases import login_user, register_user
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, data.email, data.password)

    if not user:
        raise HTTPException(status_code=400, detail="User already exists")

    return {
        "message": "User created successfully",
        "email": user.email
    }

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, data.email, data.password)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return current_user