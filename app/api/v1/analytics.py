from fastapi import APIRouter, Depends
from app.deps import get_current_user, get_current_org, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.analytics_service import AnalyticsService


analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get("/deals/summary")
async def deals_summary(
    user=Depends(get_current_user),
    org=Depends(get_current_org),
    session: AsyncSession = Depends(get_db),
):
    """Get summary statistics for deals in the organization."""
    service = AnalyticsService(session)
    return await service.deals_summary(org.id)


@analytics_router.get("/deals/funnel")
async def deals_funnel(
    user=Depends(get_current_user),
    org=Depends(get_current_org),
    session: AsyncSession = Depends(get_db),
):
    """Get deals funnel data for the organization."""
    service = AnalyticsService(session)
    return await service.deals_funnel(org.id)
