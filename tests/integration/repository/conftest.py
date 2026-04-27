import os

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.repositories.sql_order_repository import SqlOrderRepository


def _get_test_database_url() -> str | None:
    return os.environ.get("TEST_DATABASE_URL")


@pytest_asyncio.fixture
async def sql_order_repository() -> SqlOrderRepository:
    url = _get_test_database_url()
    if not url:
        pytest.skip(
            "Defina TEST_DATABASE_URL (ex.: postgresql+asyncpg://user:pass@localhost:port/db) "
            "e rode alembic upgrade head antes de executar estes testes"
        )
    engine = create_async_engine(url, echo=False)
    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    try:
        async with session_maker() as session:
            repository = SqlOrderRepository(session)
            yield repository
            await session.execute(
                text("TRUNCATE order_items, orders RESTART IDENTITY CASCADE")
            )
            await session.commit()
    finally:
        await engine.dispose()
