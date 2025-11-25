from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, get_current_user, oauth2_scheme
from app.repositories.org_repo import OrgRepository
from app.schemas.organization import OrganizationOut

organizations_router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
    dependencies=[Depends(oauth2_scheme)],
)


@organizations_router.get("/me", response_model=list[OrganizationOut])
async def my_orgs(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get organizations for the current user."""
    orgs = await OrgRepository(db).list_user_orgs(current_user.id)
    return orgs
