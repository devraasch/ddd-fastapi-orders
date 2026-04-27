import pytest

from app.application.use_cases.list_orders import ListOrders
from app.domain.entities.order import Order
from tests.mocks.fake_order_repository import FakeOrderRepository


@pytest.mark.asyncio
async def test_empty_repo_returns_empty_list(
    order_list: ListOrders,
) -> None:
    result = await order_list.execute()
    assert result == []


@pytest.mark.asyncio
async def test_single_order_appears(
    order_list: ListOrders,
    fake_order_repository: FakeOrderRepository,
) -> None:
    await fake_order_repository.create(Order(id=None, customer_name="A"))
    result = await order_list.execute()
    assert len(result) == 1


@pytest.mark.asyncio
async def test_orders_are_sorted_by_id(
    order_list: ListOrders,
    fake_order_repository: FakeOrderRepository,
) -> None:
    await fake_order_repository.create(Order(id=None, customer_name="First"))
    await fake_order_repository.create(Order(id=None, customer_name="Second"))
    result = await order_list.execute()
    assert result[0].customer_name == "First"
