from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.event_publisher import EventPublisherPort
from app.application.use_cases.create_order import CreateOrderUseCase
from app.domain.repositories.order_repository import OrderRepository
from app.infrastructure.database.base import async_session_maker
from app.infrastructure.repositories.sql_order_repository import SqlOrderRepository


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


def get_event_publisher(request: Request) -> EventPublisherPort:
    return request.app.state.event_publisher


def get_order_repository(
    db: AsyncSession = Depends(get_db),
) -> OrderRepository:
    return SqlOrderRepository(db)


def get_create_order_use_case(
    order_repository: OrderRepository = Depends(get_order_repository),
    event_publisher: EventPublisherPort = Depends(get_event_publisher),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(
        order_repository=order_repository,
        event_publisher=event_publisher,
    )
