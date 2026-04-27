from app.domain.entities.order import Order
from app.domain.repositories.order_repository import OrderRepository


class FakeOrderRepository(OrderRepository):
    """Armazenamento em memória para testes — sem SQLAlchemy."""

    def __init__(self) -> None:
        self._next_id = 0
        self.created: list[Order] = []

    def create(self, order: Order) -> Order:
        self._next_id += 1
        persisted = Order(
            id=self._next_id,
            customer_name=order.customer_name,
            total=order.total,
            status=order.status,
        )
        self.created.append(persisted)
        return persisted
