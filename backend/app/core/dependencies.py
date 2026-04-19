from typing import Callable
from uuid import UUID

from app.core.security import get_current_user
from app.modules.users.domain.entities import ResolvedRole
from fastapi import Depends, HTTPException, status


def _role_checker(*allowed_roles: ResolvedRole) -> Callable:
    def checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        is_approved = current_user.get("is_approved", True)
        allowed_values = {r.value for r in allowed_roles}

        if user_role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required: {[r.value for r in allowed_roles]}",
            )

        if user_role == ResolvedRole.OPERATOR.value and not is_approved:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your operator account is pending admin approval.",
            )

        return current_user

    return checker


# ------------------------------------------------------------------ #
# Ready-made dependencies                                              #
# ------------------------------------------------------------------ #

require_auth      = get_current_user
require_passenger = _role_checker(ResolvedRole.PASSENGER)
require_operator  = _role_checker(ResolvedRole.OPERATOR)
require_admin     = _role_checker(ResolvedRole.ADMIN)
require_operator_or_admin = _role_checker(ResolvedRole.OPERATOR, ResolvedRole.ADMIN)