from app.core.database import get_db
from app.modules.users.application.schemas import (LoginRequest,
                                                   RegisterRequest,
                                                   TokenResponse)
from app.modules.users.application.use_cases import (LoginUserUseCase,
                                                     RegisterUserUseCase)
from app.modules.users.infrastructure.repository_impl import SQLUserRepository
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_repo(db: Session = Depends(get_db)) -> SQLUserRepository:
    return SQLUserRepository(db)


@router.post("/register", response_model=TokenResponse)
def register(
    data: RegisterRequest,
    repo: SQLUserRepository = Depends(get_user_repo),
):
    result = RegisterUserUseCase(repo).execute(data.email, data.password)
    if not result:
        raise HTTPException(status_code=400, detail="Email already registered")
    return result


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    repo: SQLUserRepository = Depends(get_user_repo),
):
    result = LoginUserUseCase(repo).execute(data.email, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result