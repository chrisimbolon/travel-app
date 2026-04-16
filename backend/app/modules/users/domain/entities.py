# modules/users/domain/entities.py
import uuid
from datetime import datetime


class User:
    def __init__(
        self,
        id,
        email,
        hashed_password,
        is_active=True,
        created_at=None,
    ):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()

    @classmethod
    def create(cls, email: str, hashed_password: str):
        return cls(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hashed_password,
            is_active=True,
        )