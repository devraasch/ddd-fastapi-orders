from app.domain.entities.order import Order
from app.domain.entities.order_item import OrderItem
from app.domain.repositories.order_repository import OrderRepository


class FakeOrderRepository(OrderRepository):
    def __init__(self) -> None:
        self._next_id = 0
        self.created: list[Order] = []

    async def create(self, order: Order) -> Order:
        self._next_id += 1
        persisted = Order(
            id=self._next_id,
            customer_name=order.customer_name,
            status=order.status,
            items=[
                OrderItem(
                    product_id=i.product_id,
                    quantity=i.quantity,
                    unit_price=i.unit_price,
                )
                for i in order.items
            ],
        )
        self.created.append(persisted)
        return persisted
