from app.core.database import get_db
from app.modules.auth.application.schemas import LoginRequest, TokenResponse
from app.modules.auth.application.use_cases import login_user
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    token = login_user(db, request.email, request.password)

    return TokenResponse(access_token=token)