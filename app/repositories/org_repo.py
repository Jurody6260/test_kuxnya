from typing import Optional, Sequence

from sqlalchemy import select
from app.models.models import Organization, OrganizationMember
from app.repositories import BaseRepository
from app.repositories.org_member_repo import OrganizationMemberRepository


class OrgRepository(BaseRepository[Organization]):
    model = Organization

    async def add_member(
        self, org_id: int, user_id: int, role: str = "member"
    ):
        """Add a member to an organization with a specific role."""
        await OrganizationMemberRepository(self.session).create_from_payload(
            organization_id=org_id, user_id=user_id, role=role
        )

    async def get_member(
        self, user_id: int, org_id: int
    ) -> Optional[OrganizationMember]:
        """Get a specific member of an organization."""
        q = await self.session.execute(
            select(OrganizationMember).filter_by(
                user_id=user_id, organization_id=org_id
            )
        )
        return q.scalar_one_or_none()

    async def user_in_org(self, user_id: int, org_id: int) -> bool:
        """Check if a user is a member of an organization."""
        mem = await self.get_member(user_id, org_id)
        return mem is not None

    async def list_members(self, org_id: int):
        """List all members of an organization."""
        q = await self.session.execute(
            select(OrganizationMember).filter_by(organization_id=org_id)
        )
        return q.scalars().all()

    async def list_user_orgs(self, user_id: int) -> Sequence[Organization]:
        """List all organizations a user belongs to."""
        q = await self.session.execute(
            select(Organization)
            .join(OrganizationMember)
            .filter(OrganizationMember.user_id == user_id)
        )
        return q.scalars().all()
