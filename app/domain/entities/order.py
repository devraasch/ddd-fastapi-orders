from dataclasses import dataclass, field

from app.domain.entities.order_item import OrderItem
from app.domain.exceptions import (
    CannotCancelOrderError,
    CannotConfirmOrderError,
    OrderMutationNotAllowed,
)
from app.domain.value_objects.order_status import OrderStatus


@dataclass
class Order:
    id: int | None
    customer_name: str
    status: OrderStatus = OrderStatus.PENDING
    items: list[OrderItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.items = list(self.items)

    @property
    def total(self) -> float:
        return sum(item.line_total for item in self.items)

    def add_item(
        self,
        product_id: int,
        quantity: int,
        unit_price: float,
    ) -> None:
        self._ensure_can_mutate_items()
        self.items.append(OrderItem(product_id=product_id, quantity=quantity, unit_price=unit_price))

    def remove_item(self, product_id: int) -> None:
        self._ensure_can_mutate_items()
        for i, line in enumerate(self.items):
            if line.product_id == product_id:
                del self.items[i]
                return

    def _ensure_can_mutate_items(self) -> None:
        if self.status is not OrderStatus.PENDING:
            raise OrderMutationNotAllowed("items can only change while the order is pending")

    def confirm(self) -> None:
        if self.status is not OrderStatus.PENDING:
            raise CannotConfirmOrderError(
                f"order cannot be confirmed in state {self.status.value}"
            )
        if not self.items:
            raise CannotConfirmOrderError("cannot confirm an order with no items")
        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status is OrderStatus.CANCELLED:
            raise CannotCancelOrderError("order is already cancelled")
        self.status = OrderStatus.CANCELLED
