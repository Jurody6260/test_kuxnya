from sqlalchemy import Select, select
from typing import Any, Optional, Sequence, Tuple, Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Optional[T]:
        """Get a subject by its ID."""
        q = await self.session.execute(select(self.model).filter_by(id=id))
        return q.scalar_one_or_none()

    async def list_all(self) -> Sequence[T]:
        """List all subjects."""
        q = await self.session.execute(select(self.model))
        return q.scalars().all()

    async def list_by(self, **filters: Any) -> Sequence[T]:
        """List subjects filtered by given criteria."""
        q = await self.session.execute(select(self.model).filter_by(**filters))
        return q.scalars().all()

    async def apply_filters(
        self, **filters: Any
    ) -> Optional[Select[Tuple[T]]]:
        """Apply filters to a query."""
        query = select(self.model)
        for attr, value in filters.items():
            query = query.filter(getattr(self.model, attr) == value)
        return query

    async def create(self, subject: T) -> T:
        """Create a new subject."""
        self.session.add(subject)
        await self.session.flush()
        return subject

    async def create_from_payload(self, **payload: Any) -> T:
        """Create a new subject from payload."""
        subject = self.model(**payload)  # type: ignore
        self.session.add(subject)
        await self.session.flush()
        return subject

    async def delete(self, subject: T):
        """Delete a subject."""
        await self.session.delete(subject)
        await self.session.flush()

    async def update(self, subject: T, **payload: Any) -> T:
        """Update a subject with given payload."""
        for key, value in payload.items():
            setattr(subject, key, value)
        self.session.add(subject)
        await self.session.flush()
        return subject

    async def update_by_object(self, subject: T, **payload: Any) -> T:
        """Update a subject with given payload."""
        for key, value in payload.items():
            setattr(subject, key, value)
        self.session.add(subject)
        await self.session.flush()
        return subject
