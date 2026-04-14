from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    is_active: bool
    created_at: datetime

    @staticmethod
    def create(email: str, hashed_password: str) -> "User":
        return User(
            id=uuid4(),
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow(),
        )