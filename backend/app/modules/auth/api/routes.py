import os
from uuid import UUID

from app.core.database import get_db
from app.modules.auth.application.schemas import (OTPRequest, OTPVerify,
                                                  PasswordLoginRequest,
                                                  RefreshRequest,
                                                  TokenResponse)
from app.modules.users.application.use_cases import (LoginWithPasswordUseCase,
                                                     RequestOtpUseCase,
                                                     VerifyOtpUseCase)
from app.modules.users.domain.entities import DomainError
from app.modules.users.infrastructure.notifier import (ConsoleOtpNotifier,
                                                       WhatsAppOtpNotifier)
from app.modules.users.infrastructure.repository_impl import (
    RedisOtpRepository, SQLOperatorProfileRepository, SQLUserRepository)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_notifier():
    wa_url = os.getenv("WHATSAPP_API_URL")
    wa_token = os.getenv("WHATSAPP_API_TOKEN")
    if wa_url and wa_token:
        return WhatsAppOtpNotifier(api_url=wa_url, api_token=wa_token)
    return ConsoleOtpNotifier()


# ------------------------------------------------------------------ #
# Passenger — OTP flow                                                 #
# ------------------------------------------------------------------ #

@router.post("/request-otp", status_code=200)
async def request_otp(body: OTPRequest):
    """
    Step 1 — sends OTP via WhatsApp (console in dev).
    Always returns 200 — prevents phone enumeration.
    """
    try:
        await RequestOtpUseCase(
            otp_repo=RedisOtpRepository(),
            notifier=_get_notifier(),
        ).execute(phone=body.phone)
    except Exception:
        pass  # swallow silently — never expose errors here
    return {"message": "OTP sent successfully"}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    body: OTPVerify,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 2 — verifies OTP. Auto-creates passenger account on first login.
    Returns access + refresh tokens.
    """
    try:
        return await VerifyOtpUseCase(
            user_repo=SQLUserRepository(db),
            otp_repo=RedisOtpRepository(),
            operator_profile_repo=SQLOperatorProfileRepository(db),
        ).execute(phone=body.phone, otp_code=body.otp_code)
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


# ------------------------------------------------------------------ #
# Operator / Admin — email + password flow                            #
# ------------------------------------------------------------------ #

@router.post("/login", response_model=TokenResponse)
async def login_with_password(
    body: PasswordLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Operator and Admin login — email + password only.
    Passengers cannot use this endpoint.
    """
    try:
        return await LoginWithPasswordUseCase(
            user_repo=SQLUserRepository(db),
            operator_profile_repo=SQLOperatorProfileRepository(db),
        ).execute(email=body.email, password=body.password)
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


# ------------------------------------------------------------------ #
# Shared — token refresh                                               #
# ------------------------------------------------------------------ #

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Exchange a refresh token for a new access + refresh token pair.
    Works for both passengers and operators.
    """
    from app.core.security import (ALGORITHM, SECRET_KEY, create_access_token,
                                   create_refresh_token)
    from jose import JWTError, jwt

    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Re-resolve role from DB so revoked operators get fresh state
    user_repo = SQLUserRepository(db)
    op_repo = SQLOperatorProfileRepository(db)

    user = await user_repo.get_by_id(UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or suspended",
        )

    from app.modules.users.application.use_cases import _resolve_role
    profile = await op_repo.get_by_user_id(user.id)
    role, is_approved, profile_id = _resolve_role(user.is_admin, profile)

    return {
        "access_token": create_access_token(
            user_id=str(user.id),
            role=role.value,
            operator_profile_id=profile_id,
            is_approved=is_approved,
        ),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
        "role": role.value,
    }