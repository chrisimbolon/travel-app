from uuid import UUID

from app.core.security import (create_access_token, create_refresh_token,
                               hash_password, verify_password)
from app.modules.users.domain.entities import (DomainError, Driver,
                                               OperatorProfile, OtpCode,
                                               ResolvedRole, User)
from app.modules.users.domain.repositories import (DriverRepository,
                                                   OperatorProfileRepository,
                                                   OtpRepository,
                                                   UserRepository)
from app.modules.users.infrastructure.notifier import OtpNotifier


def _resolve_role(
    is_admin: bool,
    operator_profile: OperatorProfile | None,
) -> tuple[ResolvedRole, bool, str | None]:
    if is_admin:
        return ResolvedRole.ADMIN, True, None
    if operator_profile:
        return ResolvedRole.OPERATOR, operator_profile.is_approved, str(operator_profile.id)
    return ResolvedRole.PASSENGER, True, None


def _build_token_response(
    user: User,
    role: ResolvedRole,
    is_approved: bool,
    profile_id: str | None,
) -> dict:
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


# ------------------------------------------------------------------ #
# Passenger path — OTP                                                 #
# ------------------------------------------------------------------ #

class RequestOtpUseCase:
    def __init__(self, otp_repo: OtpRepository, notifier: OtpNotifier):
        self.otp_repo = otp_repo
        self.notifier = notifier

    async def execute(self, phone: str) -> None:
        otp = OtpCode.generate(phone)
        await self.otp_repo.store(otp)
        await self.notifier.send_otp(phone, otp.code)


class VerifyOtpUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        otp_repo: OtpRepository,
        operator_profile_repo: OperatorProfileRepository,
    ):
        self.user_repo = user_repo
        self.otp_repo = otp_repo
        self.operator_profile_repo = operator_profile_repo

    async def execute(self, phone: str, otp_code: str) -> dict:
        stored = await self.otp_repo.get(phone)
        if not stored:
            raise DomainError("OTP not found or already used")
        if stored.is_expired():
            await self.otp_repo.delete(phone)
            raise DomainError("OTP has expired")
        if not stored.matches(otp_code):
            raise DomainError("Invalid OTP code")

        await self.otp_repo.delete(phone)

        user, _ = await self.user_repo.get_or_create_by_phone(phone)
        if not user.is_active:
            raise DomainError("This account has been suspended")

        # Guard — a password user cannot log in via OTP
        if user.is_password_user:
            raise DomainError("This account uses email and password to log in")

        profile = await self.operator_profile_repo.get_by_user_id(user.id)
        role, is_approved, profile_id = _resolve_role(user.is_admin, profile)

        return _build_token_response(user, role, is_approved, profile_id)


# ------------------------------------------------------------------ #
# Operator / Admin path — email + password                            #
# ------------------------------------------------------------------ #

class LoginWithPasswordUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        operator_profile_repo: OperatorProfileRepository,
    ):
        self.user_repo = user_repo
        self.operator_profile_repo = operator_profile_repo

    async def execute(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)

        # Deliberately vague — never reveal whether email exists
        if not user or not user.hashed_password:
            raise DomainError("Invalid email or password")
        if not verify_password(password, user.hashed_password):
            raise DomainError("Invalid email or password")
        if not user.is_active:
            raise DomainError("This account has been suspended")

        # Guard — a phone-only user cannot log in via password
        if user.is_phone_user:
            raise DomainError("This account uses phone OTP to log in")

        profile = await self.operator_profile_repo.get_by_user_id(user.id)
        role, is_approved, profile_id = _resolve_role(user.is_admin, profile)

        return _build_token_response(user, role, is_approved, profile_id)


class CreateOperatorUserUseCase:
    """
    Admin creates an operator's app account (email + password)
    then links it to their OperatorProfile in one flow.
    """
    def __init__(
        self,
        user_repo: UserRepository,
        operator_profile_repo: OperatorProfileRepository,
    ):
        self.user_repo = user_repo
        self.operator_profile_repo = operator_profile_repo

    async def execute(
        self,
        email: str,
        password: str,
        name: str,
        business_name: str,
        business_phone: str,
        admin_id: UUID,
    ) -> OperatorProfile:
        # Check email not already taken
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise DomainError("Email already registered")

        # Create user
        user = User.create_operator(
            email=email,
            hashed_password=hash_password(password),
            name=name,
        )
        saved_user = await self.user_repo.save(user)

        # Create and immediately approve operator profile
        profile = OperatorProfile.create(
            user_id=saved_user.id,
            business_name=business_name,
            phone=business_phone,
        )
        profile.approve(admin_id=admin_id)
        return await self.operator_profile_repo.save(profile)


# ------------------------------------------------------------------ #
# Shared admin use cases                                               #
# ------------------------------------------------------------------ #

class RevokeOperatorUseCase:
    def __init__(self, repo: OperatorProfileRepository):
        self.repo = repo

    async def execute(self, profile_id: UUID) -> OperatorProfile:
        profile = await self.repo.get_by_id(profile_id)
        if not profile:
            raise DomainError(f"Operator profile {profile_id} not found")
        profile.revoke()
        return await self.repo.update(profile)


class ReApproveOperatorUseCase:
    def __init__(self, repo: OperatorProfileRepository):
        self.repo = repo

    async def execute(self, profile_id: UUID, admin_id: UUID) -> OperatorProfile:
        profile = await self.repo.get_by_id(profile_id)
        if not profile:
            raise DomainError(f"Operator profile {profile_id} not found")
        if profile.is_approved:
            raise DomainError("Operator is already approved")
        profile.approve(admin_id=admin_id)
        return await self.repo.update(profile)


class CreateDriverUseCase:
    def __init__(
        self,
        driver_repo: DriverRepository,
        operator_profile_repo: OperatorProfileRepository,
    ):
        self.driver_repo = driver_repo
        self.operator_profile_repo = operator_profile_repo

    async def execute(
        self,
        operator_profile_id: UUID,
        name: str,
        phone: str,
        licence_number: str | None = None,
        linked_user_id: UUID | None = None,
    ) -> Driver:
        profile = await self.operator_profile_repo.get_by_id(operator_profile_id)
        if not profile or not profile.is_approved:
            raise DomainError("Operator profile not found or not approved")
        driver = Driver.create(
            operator_id=operator_profile_id,
            name=name,
            phone=phone,
            licence_number=licence_number,
            linked_user_id=linked_user_id,
        )
        return await self.driver_repo.save(driver)