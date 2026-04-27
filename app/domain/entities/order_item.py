from dataclasses import dataclass

from app.domain.exceptions import InvalidOrderItemError


@dataclass
class OrderItem:
    product_id: int
    quantity: int
    unit_price: float

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidOrderItemError("quantity must be greater than zero")
        if self.unit_price < 0:
            raise InvalidOrderItemError("unit_price cannot be negative")

    @property
    def line_total(self) -> float:
        return self.quantity * self.unit_price
