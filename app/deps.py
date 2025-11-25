from typing import Annotated, TYPE_CHECKING
from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.core.security import decode_token
from app.repositories.org_member_repo import OrganizationMemberRepository
from app.repositories.user_repo import UserRepository
from app.repositories.org_repo import OrgRepository

if TYPE_CHECKING:
    from app.models.models import User
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> "User":
    """Get the current authenticated user based on the Authorization header."""
    print(f"Token: {token}")
    if not token:
        raise HTTPException(
            status_code=401, detail="Missing authorization header"
        )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid auth header")

    sub = payload.get("sub")
    user = None

    if sub:
        user_id = int(sub)
        user = await UserRepository(db).get(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def get_current_org(
    current_user: "User" = Depends(get_current_user),
    x_org_id: int | None = Header(None, alias="X-Organization-Id"),
    session: AsyncSession = Depends(get_db),
):
    """Get the current organization based on X-Organization-Id header."""

    if not x_org_id:
        raise HTTPException(
            status_code=400, detail="X-Organization-Id header required"
        )

    org_repo = OrgRepository(session)
    org = await org_repo.get(x_org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    mem_repo = OrganizationMemberRepository(session)
    membership = await mem_repo.get_by_user_and_org(current_user.id, org.id)
    if not membership:
        raise HTTPException(
            status_code=403, detail="Not allowed in this organization"
        )

    return org
