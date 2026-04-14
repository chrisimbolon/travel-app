from app.modules.auth.infrastructure.security import (create_access_token,
                                                      verify_password)
from app.modules.users.infrastructure.models import UserModel
from fastapi import HTTPException
from sqlalchemy.orm import Session


def login_user(db: Session, email: str, password: str) -> str:
    user = db.query(UserModel).filter(UserModel.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return token