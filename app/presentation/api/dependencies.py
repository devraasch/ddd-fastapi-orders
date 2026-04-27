from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.application.ports.event_publisher import EventPublisherPort
from app.application.use_cases.create_order import CreateOrderUseCase
from app.domain.repositories.order_repository import OrderRepository
from app.infrastructure.database.base import SessionLocal
from app.infrastructure.repositories.sql_order_repository import SqlOrderRepository


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_event_publisher(request: Request) -> EventPublisherPort:
    return request.app.state.event_publisher


def get_order_repository(
    db: Session = Depends(get_db),
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
