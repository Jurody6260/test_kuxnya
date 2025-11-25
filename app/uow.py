from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

        @asynccontextmanager
        async def begin(self):
            try:
                async with self.session.begin():
                    yield self
            except Exception:
                await self.session.rollback()
                raise
