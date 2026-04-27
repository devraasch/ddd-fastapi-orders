from abc import ABC, abstractmethod

from app.domain.entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def create(self, order: Order) -> Order: ...
