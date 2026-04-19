from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.modules.users.application.schemas import (CreateOperatorRequest,
                                                   OperatorProfileResponse)
from app.modules.users.application.use_cases import (CreateOperatorUserUseCase,
                                                     ReApproveOperatorUseCase,
                                                     RevokeOperatorUseCase)
from app.modules.users.domain.entities import DomainError
from app.modules.users.infrastructure.repository_impl import (
    SQLOperatorProfileRepository, SQLUserRepository)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/admin", tags=["admin"])


def get_repos(db: AsyncSession = Depends(get_db)):
    return SQLUserRepository(db), SQLOperatorProfileRepository(db)


def _to_response(p) -> OperatorProfileResponse:
    return OperatorProfileResponse(
        id=p.id,
        user_id=p.user_id,
        business_name=p.business_name,
        phone=p.phone,
        is_approved=p.is_approved,
        approved_at=p.approved_at,
        created_at=p.created_at,
    )


@router.post(
    "/operators",
    response_model=OperatorProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_operator(
    data: CreateOperatorRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Admin creates an operator account — user + profile in one call.
    Operator receives their email + password out-of-band (e.g. by WhatsApp).
    """
    user_repo = SQLUserRepository(db)
    op_repo = SQLOperatorProfileRepository(db)
    try:
        profile = await CreateOperatorUserUseCase(user_repo, op_repo).execute(
            email=data.email,
            password=data.password,
            name=data.name,
            business_name=data.business_name,
            business_phone=data.business_phone,
            admin_id=UUID(current_user["user_id"]),
        )
        return _to_response(profile)
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/operators/{profile_id}/revoke", response_model=OperatorProfileResponse)
async def revoke_operator(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    op_repo = SQLOperatorProfileRepository(db)
    try:
        return _to_response(await RevokeOperatorUseCase(op_repo).execute(profile_id))
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/operators/{profile_id}/approve", response_model=OperatorProfileResponse)
async def reapprove_operator(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    op_repo = SQLOperatorProfileRepository(db)
    try:
        return _to_response(
            await ReApproveOperatorUseCase(op_repo).execute(
                profile_id=profile_id,
                admin_id=UUID(current_user["user_id"]),
            )
        )
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/operators/pending", response_model=list[OperatorProfileResponse])
async def list_pending(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin),
):
    op_repo = SQLOperatorProfileRepository(db)
    return [_to_response(p) for p in await op_repo.list_pending()]