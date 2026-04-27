import pytest

from app.application.use_cases.create_order import CreateOrder
from app.domain.value_objects.order_status import OrderStatus
from tests.mocks.fake_event_publisher import FakeEventPublisher
from tests.mocks.fake_order_repository import FakeOrderRepository

_ONE_LINE: list[tuple[int, int, float]] = [(1, 1, 0.0)]


@pytest.mark.asyncio
async def test_creates_with_status_pending(
    order_create: CreateOrder,
) -> None:
    result = await order_create.execute(
        customer_name="Maria",
        items=_ONE_LINE,
    )
    assert result.status is OrderStatus.PENDING


@pytest.mark.asyncio
async def test_creates_with_total_from_items(
    order_create: CreateOrder,
) -> None:
    result = await order_create.execute(
        customer_name="Maria",
        items=[(1, 2, 5.0), (2, 1, 3.0)],
    )
    assert result.total == 13.0


@pytest.mark.asyncio
async def test_persists_one_order_in_repository(
    order_create: CreateOrder,
    fake_order_repository: FakeOrderRepository,
) -> None:
    await order_create.execute(customer_name="Maria", items=_ONE_LINE)
    assert len(fake_order_repository.created) == 1


@pytest.mark.asyncio
async def test_publishes_order_created(
    order_create: CreateOrder,
    fake_event_publisher: FakeEventPublisher,
) -> None:
    await order_create.execute(
        customer_name="Maria",
        items=[(5, 1, 2.0)],
    )
    assert fake_event_publisher.published == [
        (
            "order.created",
            {
                "id": 1,
                "customer_name": "Maria",
                "total": 2.0,
                "status": "PENDING",
            },
        )
    ]
