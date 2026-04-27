from abc import ABC, abstractmethod

from app.domain.entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    async def create(self, order: Order) -> Order: ...

    @abstractmethod
    async def get_by_id(self, order_id: int) -> Order | None: ...

    @abstractmethod
    async def list_all(self) -> list[Order]: ...

    @abstractmethod
    async def update(self, order: Order) -> Order | None: ...
