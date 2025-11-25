from datetime import datetime
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from app.core.config import settings

async_engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


# Можно было бы использовать миксины, но для простоты используем базовый класс.
class Base(DeclarativeBase):
    """
    Declarative base that provides common columns for all models:
      - id (primary key)
      - created_at (timestamp)
    Subclasses (models) inherit these columns automatically.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
