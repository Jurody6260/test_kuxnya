from datetime import datetime
from typing import Sequence
from sqlalchemy import select
from app.models.models import Deal, Task
from app.repositories import BaseRepository


class TaskRepository(BaseRepository[Task]):
    model = Task

    async def list_by_deal(self, deal_id: int):
        """List tasks by deal ID."""
        q = await self.session.execute(
            select(self.model).filter_by(deal_id=deal_id)
        )
        return q.scalars().all()

    async def list_by_org(
        self,
        *,
        org_id: int,
        only_open: bool = True,
        due_before: datetime | None = None,
        due_after: datetime | None = None,
    ) -> Sequence[Task]:
        """List tasks by organization ID."""
        ffilters = [Deal.organization_id == org_id]
        if only_open:
            ffilters.append(Task.is_done.is_(False))
        if due_before is not None:
            ffilters.append(Task.due_date <= due_before)
        if due_after is not None:
            ffilters.append(Task.due_date >= due_after)
        q = await self.session.execute(
            select(Task).join(Deal, Task.deal_id == Deal.id).filter(*ffilters)
        )
        return q.scalars().all()
