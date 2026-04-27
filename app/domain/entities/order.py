from dataclasses import dataclass


@dataclass
class Order:
    id: int | None
    customer_name: str
    total: float
    status: str = "PENDING"
