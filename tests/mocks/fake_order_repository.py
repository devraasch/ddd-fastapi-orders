from app.domain.entities.order import Order
from app.domain.entities.order_item import OrderItem
from app.domain.repositories.order_repository import OrderRepository


class FakeOrderRepository(OrderRepository):
    def __init__(self) -> None:
        self._next_id = 0
        self.created: list[Order] = []
        self._by_id: dict[int, Order] = {}

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
        self._by_id[persisted.id] = persisted
        return persisted

    async def get_by_id(self, order_id: int) -> Order | None:
        return self._by_id.get(order_id)

    async def list_all(self) -> list[Order]:
        return sorted(self._by_id.values(), key=lambda o: o.id or 0)

    async def update(self, order: Order) -> Order | None:
        if order.id is None:
            raise ValueError("order id is required to update")
        if order.id not in self._by_id:
            return None
        persisted = Order(
            id=order.id,
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
        self._by_id[order.id] = persisted
        return persisted
