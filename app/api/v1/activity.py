from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_current_org, get_current_user, get_db
from app.repositories.activity_repo import ActivityRepository
from app.services.activity_service import ActivityService

from app.schemas.activity import ActivityCreate, ActivityOut


activities_router = APIRouter(prefix="/deals", tags=["Activities"])


@activities_router.get(
    "/{deal_id}/activities", response_model=list[ActivityOut]
)
async def list_contacts(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org=Depends(get_current_org),
):
    """List activities for a specific deal."""
    repo = ActivityRepository(db)
    contacts = await repo.list_by_deal(
        deal_id,
    )
    return contacts


@activities_router.post(
    "/{deal_id}/activities", response_model=ActivityOut, status_code=201
)
async def create_activity(
    deal_id: int,
    payload: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org=Depends(get_current_org),
):
    """Create an activity for a specific deal."""
    svc = ActivityService(ActivityRepository(db))
    activity = await svc.create(
        user=current_user,
        deal_id=deal_id,
        payload=payload,
    )
    return activity
