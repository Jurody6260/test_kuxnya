from sqlalchemy import select
from app.models.models import User
from app.repositories import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str):
        """Get user by email."""
        q = await self.session.execute(
            select(self.model).filter_by(email=email),
        )
        return q.scalar_one_or_none()
