# modules/users/application/use_cases.py
from app.core.security import (create_access_token, hash_password,
                               verify_password)

from ..domain.entities import User
from ..domain.repositories import UserRepository


class RegisterUserUseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self, email: str, password: str):
        existing = self.repo.get_by_email(email)
        if existing:
            return None

        hashed = hash_password(password)

        user = User.create(
            email=email,
            hashed_password=hashed
        )

        self.repo.save(user)

        token = create_access_token({"sub": str(user.id)})

        return {
            "access_token": token,
            "token_type": "bearer",
        }


class LoginUserUseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self, email: str, password: str):
        user = self.repo.get_by_email(email)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        token = create_access_token({"sub": str(user.id)})

        return {
            "access_token": token,
            "token_type": "bearer",
        }