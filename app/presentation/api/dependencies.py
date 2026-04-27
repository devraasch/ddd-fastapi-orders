from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.event_publisher import EventPublisherPort
from app.application.use_cases.cancel_order import CancelOrder
from app.application.use_cases.confirm_order import ConfirmOrder
from app.application.use_cases.create_order import CreateOrder
from app.application.use_cases.get_order import GetOrder
from app.application.use_cases.list_orders import ListOrders
from app.domain.repositories.order_repository import OrderRepository
from app.infrastructure.database.base import async_session_maker
from app.infrastructure.repositories.sql_order_repository import SqlOrderRepository


async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_event_publisher(request: Request) -> EventPublisherPort:
    return request.app.state.event_publisher


def get_order_repository(
    db: AsyncSession = Depends(get_db),
) -> OrderRepository:
    return SqlOrderRepository(db)


def get_create_order(
    order_repository: OrderRepository = Depends(get_order_repository),
    event_publisher: EventPublisherPort = Depends(get_event_publisher),
) -> CreateOrder:
    return CreateOrder(
        order_repository=order_repository,
        event_publisher=event_publisher,
    )


def get_order(
    order_repository: OrderRepository = Depends(get_order_repository),
) -> GetOrder:
    return GetOrder(order_repository=order_repository)


def get_list_orders(
    order_repository: OrderRepository = Depends(get_order_repository),
) -> ListOrders:
    return ListOrders(order_repository=order_repository)


def get_confirm_order(
    order_repository: OrderRepository = Depends(get_order_repository),
    event_publisher: EventPublisherPort = Depends(get_event_publisher),
) -> ConfirmOrder:
    return ConfirmOrder(
        order_repository=order_repository,
        event_publisher=event_publisher,
    )


def get_cancel_order(
    order_repository: OrderRepository = Depends(get_order_repository),
    event_publisher: EventPublisherPort = Depends(get_event_publisher),
) -> CancelOrder:
    return CancelOrder(
        order_repository=order_repository,
        event_publisher=event_publisher,
    )
