from app.application.ports.event_publisher import EventPublisherPort
from app.domain.entities.order import Order
from app.domain.repositories.order_repository import OrderRepository


class CreateOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisherPort,
    ) -> None:
        self._order_repository = order_repository
        self._event_publisher = event_publisher

    async def execute(self, customer_name: str) -> Order:
        order = Order(
            id=None,
            customer_name=customer_name,
        )
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
