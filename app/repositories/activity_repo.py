from sqlalchemy import select
from app.models.models import Activity
from app.repositories import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    model = Activity

    async def list_by_deal(self, deal_id: int):
        """List activities by deal ID."""
        q = await self.session.execute(
            select(self.model).filter_by(deal_id=deal_id)
        )
        return q.scalars().all()

    async def create_for(
        self,
        deal_id: int,
        author_id: int | None,
        payload: dict,
        type_: str = "comment",
    ):
        act = Activity(
            deal_id=deal_id, author_id=author_id, type=type_, payload=payload
        )
        await self.create(act)
        return act
