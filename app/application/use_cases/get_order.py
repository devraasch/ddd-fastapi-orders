from app.domain.entities.order import Order
from app.domain.repositories.order_repository import OrderRepository


class GetOrder:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository = order_repository

    async def execute(self, order_id: int) -> Order | None:
        return await self._order_repository.get_by_id(order_id)
