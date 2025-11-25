from fastapi import HTTPException, status
from fastapi.params import Depends
from typing import Annotated, Iterable

from sqlalchemy import select
from app.deps import get_current_org, get_current_user
from app.models.models import Organization, OrganizationMember, RoleEnum, User
from app.repositories.org_member_repo import OrganizationMemberRepository
from sqlalchemy.ext.asyncio import AsyncSession


# Role priority: higher number == more privileges
ROLE_PRIORITY = {
    RoleEnum.member: 0,
    RoleEnum.manager: 1,
    RoleEnum.admin: 2,
    RoleEnum.owner: 3,
}


def _role_to_enum(role: RoleEnum | str) -> RoleEnum:
    if isinstance(role, RoleEnum):
        return role
    return RoleEnum(role)


def _role_value(role: RoleEnum | str) -> int:
    try:
        return ROLE_PRIORITY[_role_to_enum(role)]
    except Exception:
        raise ValueError(f"Unknown role: {role}")


class RoleChecker:
    """
    FastAPI dependency callable.

    Usage examples:
        # allowed roles list (exact match on string) # type: ignore
      - Depends(RoleChecker(session, ["owner"]))
        # same as above
      - Depends(RoleChecker(session, [RoleEnum.admin]))
        # minimum role: manager OR higher (admin, owner)
      - Depends(RoleChecker(session, RoleEnum.manager))
        # same as above
      - Depends(RoleChecker(session, "manager"))
    """

    def __init__(
        self,
        session: AsyncSession,
        allowed_roles: RoleEnum | str | Iterable[str],
    ):
        self.allowed_roles = allowed_roles
        self.session = session

    async def __call__(
        self,
        user: Annotated[User, Depends(get_current_user)],
        org: Annotated[Organization, Depends(get_current_org)],
    ):
        repo = OrganizationMemberRepository(self.session)
        org_mem = await repo.get_by_user_and_org(user.id, org.id)

        if org_mem is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization member not found",
            )

        # If allowed_roles is an iterable (list/tuple/set),
        # treat it as explicit allowed role names
        if isinstance(self.allowed_roles, Iterable) and not isinstance(
            self.allowed_roles, (str, RoleEnum)
        ):
            if str(org_mem.role) in self.allowed_roles:
                return True
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have enough permissions",
            )

        # Otherwise treat allowed_roles as a minimum required role
        # (manager -> manager/admin/owner)
        try:
            min_role = _role_to_enum(
                self.allowed_roles
            )  # may raise ValueError
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role specification for RoleChecker",
            )

        if ROLE_PRIORITY.get(
            org_mem.role, -1  # type: ignore
        ) >= ROLE_PRIORITY.get(min_role, -1):
            return True

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have enough permissions",
        )


async def has_minimum_role(
    session: AsyncSession,
    user_id: int,
    org_id: int,
    required_role: RoleEnum | str,
) -> bool:
    """
    Returns True if the user's role is >= required_role in the hierarchy:
      member < manager < admin < owner
    """
    q = await session.execute(
        select(OrganizationMember).filter_by(
            user_id=user_id, organization_id=org_id
        )
    )
    member = q.scalar_one_or_none()
    if not member:
        return False
    try:
        return ROLE_PRIORITY.get(
            member.role, -1  # type: ignore
        ) >= _role_value(required_role)
    except ValueError:
        return False


async def is_owner(session: AsyncSession, user_id: int, org_id: int) -> bool:
    return await has_minimum_role(session, user_id, org_id, RoleEnum.owner)


async def is_admin(session: AsyncSession, user_id: int, org_id: int) -> bool:
    # admin or owner
    return await has_minimum_role(session, user_id, org_id, RoleEnum.admin)


async def is_manager(session: AsyncSession, user_id: int, org_id: int) -> bool:
    # manager or admin or owner
    return await has_minimum_role(session, user_id, org_id, RoleEnum.manager)
