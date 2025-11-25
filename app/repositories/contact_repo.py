from sqlalchemy import select
from app.models.models import Contact
from app.repositories import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    model = Contact

    async def list_by_org(
        self, org_id: int, offset: int = 0, limit: int = 20, filters: dict = {}
    ):

        q = await self.session.execute(
            select(Contact)
            .filter_by(organization_id=org_id, **filters)
            .offset(offset)
            .limit(limit)
        )
        return q.scalars().all()
