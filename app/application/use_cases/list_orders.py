from app.domain.entities.order import Order
from app.domain.repositories.order_repository import OrderRepository


class ListOrders:
    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository = order_repository

    async def execute(self) -> list[Order]:
        return await self._order_repository.list_all()
