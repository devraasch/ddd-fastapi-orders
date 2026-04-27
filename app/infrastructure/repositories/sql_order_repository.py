from sqlalchemy.orm import Session

from app.domain.entities.order import Order
from app.domain.repositories.order_repository import OrderRepository
from app.infrastructure.database.models import OrderModel


class SqlOrderRepository(OrderRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, order: Order) -> Order:
        row = OrderModel(
            customer_name=order.customer_name,
            total=order.total,
            status=order.status,
        )
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return Order(
            id=row.id,
            customer_name=row.customer_name,
            total=row.total,
            status=row.status,
        )
