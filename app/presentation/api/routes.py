from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.cancel_order import CancelOrder
from app.application.use_cases.confirm_order import ConfirmOrder
from app.application.use_cases.create_order import CreateOrder
from app.application.use_cases.get_order import GetOrder
from app.application.use_cases.list_orders import ListOrders
from app.domain.exceptions import CannotCancelOrderError, CannotConfirmOrderError
from app.presentation.api.dependencies import (
    get_cancel_order,
    get_confirm_order,
    get_create_order,
    get_list_orders,
    get_order,
)
from app.presentation.api.schemas import CreateOrderRequest, OrderResponse, order_to_response

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    payload: CreateOrderRequest,
    create: CreateOrder = Depends(get_create_order),
) -> OrderResponse:
    order = await create.execute(customer_name=payload.customer_name)
    return order_to_response(order)


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: int,
    reader: GetOrder = Depends(get_order),
) -> OrderResponse:
    order = await reader.execute(order_id=order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="order not found",
        )
    return order_to_response(order)


@router.get("/orders", response_model=list[OrderResponse])
async def list_orders(
    orders: ListOrders = Depends(get_list_orders),
) -> list[OrderResponse]:
    out = await orders.execute()
    return [order_to_response(o) for o in out]


@router.post("/orders/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: int,
    confirm: ConfirmOrder = Depends(get_confirm_order),
) -> OrderResponse:
    try:
        order = await confirm.execute(order_id=order_id)
    except CannotConfirmOrderError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="order not found",
        )
    return order_to_response(order)


@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    cancel: CancelOrder = Depends(get_cancel_order),
) -> OrderResponse:
    try:
        order = await cancel.execute(order_id=order_id)
    except CannotCancelOrderError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="order not found",
        )
    return order_to_response(order)
