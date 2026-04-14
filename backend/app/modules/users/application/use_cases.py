from passlib.context import CryptContext

from ..domain.entities import User
from ..domain.repositories import UserRepository
from .schemas import CreateUserRequest, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreateUserUseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self, request: CreateUserRequest) -> UserResponse:
        existing = self.repo.get_by_email(request.email)
        if existing:
            raise ValueError("User already exists")

        hashed_password = pwd_context.hash(request.password)

        user = User.create(
            email=request.email,
            hashed_password=hashed_password,
        )

        self.repo.save(user)

        return UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
        )