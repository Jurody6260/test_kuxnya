from typing import Sequence
from sqlalchemy import select
from app.models.models import Deal
from app.repositories import BaseRepository


class DealRepository(BaseRepository[Deal]):
    model = Deal

    async def list_by_org(
        self,
        org_id: int,
        *_,
        status: list[str] | None = None,
        stage: str | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
        owner_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order: str = "desc",
    ) -> Sequence[Deal]:
        # collect all conditions and apply them in one filter() call
        conditions = [self.model.organization_id == org_id]
        if status:
            conditions.append(self.model.status.in_(status))
        if stage is not None:
            conditions.append(self.model.stage == stage)
        if min_amount is not None:
            conditions.append(self.model.amount >= min_amount)
        if max_amount is not None:
            conditions.append(self.model.amount <= max_amount)
        if owner_id is not None:
            conditions.append(self.model.owner_id == owner_id)

        q = select(self.model).filter(*conditions)

        # order_by handling (simple, not SQL injection safe if uncontrolled)
        col = getattr(self.model, order_by, None)
        if col is not None:
            q = q.order_by(col.desc() if order == "desc" else col.asc())

        q = q.offset(offset).limit(limit)
        r = await self.session.execute(q)
        return r.scalars().all()

    async def list_by_contact(self, contact_id: int):
        """List deals by contact ID."""
        q = await self.session.execute(
            select(self.model).filter_by(contact_id=contact_id)
        )
        return q.scalars().all()
