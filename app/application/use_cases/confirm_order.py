from app.application.ports.event_publisher import EventPublisherPort
from app.domain.entities.order import Order
from app.domain.repositories.order_repository import OrderRepository


class ConfirmOrder:
    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisherPort,
    ) -> None:
        self._order_repository = order_repository
        self._event_publisher = event_publisher

    async def execute(self, order_id: int) -> Order | None:
        order = await self._order_repository.get_by_id(order_id)
        if order is None:
            return None
        order.confirm()
        updated = await self._order_repository.update(order)
        if updated is None:
            return None
        await self._event_publisher.publish(
            "order.confirmed",
            {
                "id": updated.id,
                "customer_name": updated.customer_name,
                "total": updated.total,
                "status": updated.status.value,
            },
        )
        return updated
