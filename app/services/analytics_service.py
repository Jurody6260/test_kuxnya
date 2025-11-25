from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Deal, DealStatus


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def deals_summary(self, org_id: int):
        # count, sum, won, lost, in_progress
        q = await self.session.execute(
            select(
                func.count(Deal.id),
                func.sum(Deal.amount),
                func.count().filter(Deal.status == DealStatus.won),
                func.count().filter(Deal.status == DealStatus.lost),
                func.count().filter(Deal.status == DealStatus.in_progress),
            ).filter(Deal.organization_id == org_id)
        )
        total, total_amount, won, lost, in_progress = q.one()
        return {
            "total_deals": total or 0,
            "total_amount": float(total_amount or 0),
            "won": won or 0,
            "lost": lost or 0,
            "in_progress": in_progress or 0,
        }

    async def deals_funnel(self, org_id: int):
        # group by Deal.stage
        q = await self.session.execute(
            select(Deal.stage, func.count(Deal.id))
            .filter(Deal.organization_id == org_id)
            .group_by(Deal.stage)
        )
        rows = q.all()
        return {
            "funnel": [
                {
                    "stage": stage.value if hasattr(stage, "value") else stage,
                    "count": count,
                }
                for stage, count in rows
            ]
        }
