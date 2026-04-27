import pytest

from app.application.use_cases.get_order import GetOrder
from app.domain.entities.order import Order
from app.domain.value_objects.order_status import OrderStatus
from tests.mocks.fake_order_repository import FakeOrderRepository


@pytest.mark.asyncio
async def test_returns_none_when_missing(
    order_read: GetOrder,
) -> None:
    result = await order_read.execute(order_id=99)
    assert result is None


@pytest.mark.asyncio
async def test_returns_customer_name(
    order_read: GetOrder,
    fake_order_repository: FakeOrderRepository,
) -> None:
    order = await fake_order_repository.create(
        Order(id=None, customer_name="Jo"),
    )
    result = await order_read.execute(order_id=order.id)
    assert result.customer_name == "Jo"


@pytest.mark.asyncio
async def test_returns_status_pending(
    order_read: GetOrder,
    fake_order_repository: FakeOrderRepository,
) -> None:
    order = await fake_order_repository.create(
        Order(id=None, customer_name="Jo"),
    )
    result = await order_read.execute(order_id=order.id)
    assert result.status is OrderStatus.PENDING
