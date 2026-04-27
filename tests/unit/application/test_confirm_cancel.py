import pytest

from app.application.use_cases.cancel_order import CancelOrder
from app.application.use_cases.confirm_order import ConfirmOrder
from app.domain.entities.order import Order
from app.domain.exceptions import CannotCancelOrderError, CannotConfirmOrderError
from app.domain.value_objects.order_status import OrderStatus
from tests.mocks.fake_event_publisher import FakeEventPublisher
from tests.mocks.fake_order_repository import FakeOrderRepository


@pytest.mark.asyncio
async def test_confirm_none_when_order_missing(
    order_confirm: ConfirmOrder,
) -> None:
    result = await order_confirm.execute(order_id=1)
    assert result is None


@pytest.mark.asyncio
async def test_confirm_publishes_event(
    order_confirm: ConfirmOrder,
    fake_order_repository: FakeOrderRepository,
    fake_event_publisher: FakeEventPublisher,
) -> None:
    o = Order(id=None, customer_name="Z")
    o.add_item(product_id=1, quantity=1, unit_price=2.0)
    await fake_order_repository.create(o)
    await order_confirm.execute(order_id=1)
    assert any(
        name == "order.confirmed" for name, _ in fake_event_publisher.published
    )


@pytest.mark.asyncio
async def test_confirm_fails_on_empty_order(
    order_confirm: ConfirmOrder,
    fake_order_repository: FakeOrderRepository,
) -> None:
    await fake_order_repository.create(Order(id=None, customer_name="E"))
    with pytest.raises(CannotConfirmOrderError):
        await order_confirm.execute(order_id=1)


@pytest.mark.asyncio
async def test_cancel_none_when_order_missing(
    order_cancel: CancelOrder,
) -> None:
    result = await order_cancel.execute(order_id=1)
    assert result is None


@pytest.mark.asyncio
async def test_cancel_publishes_event(
    order_cancel: CancelOrder,
    fake_order_repository: FakeOrderRepository,
    fake_event_publisher: FakeEventPublisher,
) -> None:
    await fake_order_repository.create(Order(id=None, customer_name="C"))
    await order_cancel.execute(order_id=1)
    assert any(
        p == "order.cancelled" for p, _ in fake_event_publisher.published
    )


@pytest.mark.asyncio
async def test_cancel_fails_if_already_cancelled(
    order_cancel: CancelOrder,
    fake_order_repository: FakeOrderRepository,
) -> None:
    o = await fake_order_repository.create(Order(id=None, customer_name="D"))
    loaded = await fake_order_repository.get_by_id(o.id)
    loaded.cancel()
    await fake_order_repository.update(loaded)
    with pytest.raises(CannotCancelOrderError):
        await order_cancel.execute(order_id=1)


@pytest.mark.asyncio
async def test_confirm_persists_confirmed_status(
    order_confirm: ConfirmOrder,
    fake_order_repository: FakeOrderRepository,
) -> None:
    o = Order(id=None, customer_name="Q")
    o.add_item(product_id=1, quantity=1, unit_price=1.0)
    await fake_order_repository.create(o)
    await order_confirm.execute(order_id=1)
    stored = await fake_order_repository.get_by_id(1)
    assert stored.status is OrderStatus.CONFIRMED
