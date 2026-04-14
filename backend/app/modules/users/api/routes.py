from app.core.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..application.schemas import CreateUserRequest, UserResponse
from ..application.use_cases import CreateUserUseCase
from ..infrastructure.repository_impl import SQLUserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
):
    repo = SQLUserRepository(db)
    use_case = CreateUserUseCase(repo)

    try:
        return use_case.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))