from pydantic import BaseModel, Field

from app.domain.entities.order import Order


class CreateOrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    total: float
    status: str
    items: list[OrderItemResponse]


def order_to_response(order: Order) -> OrderResponse:
    if order.id is None:
        raise ValueError("persisted order must have an id")
    return OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        total=order.total,
        status=order.status.value,
        items=[
            OrderItemResponse(
                product_id=i.product_id,
                quantity=i.quantity,
                unit_price=i.unit_price,
            )
            for i in order.items
        ],
    )
