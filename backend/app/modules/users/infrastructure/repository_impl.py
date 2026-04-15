# app/modules/users/infrastructure/repository_impl.py

from uuid import UUID

from sqlalchemy.orm import Session

from ..domain.entities import User
from ..domain.repositories import UserRepository
from .models import UserModel


class SQLUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        obj = (
            self.db.query(UserModel)
            .filter(UserModel.email == email)
            .first()
        )
        return self._to_domain(obj) if obj else None

    def get_by_id(self, user_id: UUID) -> User | None:
        obj = (
            self.db.query(UserModel)
            .filter(UserModel.id == user_id)
            .first()
        )
        return self._to_domain(obj) if obj else None

    def save(self, user: User) -> User:
        obj = UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return self._to_domain(obj)

    def _to_domain(self, obj: UserModel) -> User:
        return User(
            id=obj.id,
            email=obj.email,
            hashed_password=obj.hashed_password,
            is_active=obj.is_active,
            created_at=obj.created_at,
        )