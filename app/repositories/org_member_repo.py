from sqlalchemy import select
from app.models.models import OrganizationMember
from app.repositories import BaseRepository


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    model = OrganizationMember

    async def get_by_user_and_org(self, user_id: int, org_id: int):
        """Get organization member by user ID and organization ID."""
        q = await self.session.execute(
            select(self.model).filter_by(
                user_id=user_id, organization_id=org_id
            )
        )
        return q.scalar_one_or_none()
