from pydantic import BaseModel, Field


class CreateOrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    total: float
    status: str
