from fastapi import APIRouter, Depends

from app.application.use_cases.create_order import CreateOrderUseCase
from app.presentation.api.dependencies import get_create_order_use_case
from app.presentation.api.schemas import CreateOrderRequest, OrderResponse

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    payload: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
) -> OrderResponse:
    order = await use_case.execute(
        customer_name=payload.customer_name,
        total=payload.total,
    )
    return OrderResponse(
        id=order.id,
        customer_name=order.customer_name,
        total=order.total,
        status=order.status,
    )
