import asyncio
from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)
from httpx import AsyncClient, ASGITransport

from app import app
from app.db.base import Base, get_db
from app.core.config import settings

# -----------------------------
#  TEST DATABASE
# -----------------------------
TEST_DATABASE_URL = settings.TEST_DATABASE_URL

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    future=True,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# -----------------------------
#  event loop
# -----------------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


# -----------------------------
#  Setup DB (drop/create)
# -----------------------------
@pytest.fixture(scope="session")
async def test_db_setup_sessionmaker():
    # assert if we use TEST_DB URL for 100%
    # some other asserts...
    # async_engine = create_async_engine(...)

    # always drop and create test db tables between tests session
    async with test_engine.begin() as conn:

        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return TestSessionLocal


@pytest.fixture
async def session(
    test_db_setup_sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    async with test_db_setup_sessionmaker() as session:
        yield session


# -----------------------------
#  test client
# -----------------------------
@pytest.fixture()
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
