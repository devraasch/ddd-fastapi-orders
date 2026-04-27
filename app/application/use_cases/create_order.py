from app.application.ports.event_publisher import EventPublisherPort
from app.domain.entities.order import Order
from app.domain.repositories.order_repository import OrderRepository


class CreateOrder:
    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisherPort,
    ) -> None:
        self._order_repository = order_repository
        self._event_publisher = event_publisher

    async def execute(
        self,
        customer_name: str,
        items: list[tuple[int, int, float]],
    ) -> Order:
        order = Order(id=None, customer_name=customer_name)
        for product_id, quantity, unit_price in items:
            order.add_item(product_id, quantity, unit_price)
        created = await self._order_repository.create(order)

        await self._event_publisher.publish(
            "order.created",
            {
                "id": created.id,
                "customer_name": created.customer_name,
                "total": created.total,
                "status": created.status.value,
            },
        )

        return created
