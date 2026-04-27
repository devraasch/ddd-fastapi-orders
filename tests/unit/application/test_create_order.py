import pytest

from app.application.use_cases.create_order import CreateOrder
from app.domain.value_objects.order_status import OrderStatus
from tests.mocks.fake_event_publisher import FakeEventPublisher
from tests.mocks.fake_order_repository import FakeOrderRepository


@pytest.mark.asyncio
async def test_creates_with_status_pending(
    order_create: CreateOrder,
) -> None:
    result = await order_create.execute(customer_name="Maria")
    assert result.status is OrderStatus.PENDING


@pytest.mark.asyncio
async def test_creates_with_zero_total(
    order_create: CreateOrder,
) -> None:
    result = await order_create.execute(customer_name="Maria")
    assert result.total == 0.0


@pytest.mark.asyncio
async def test_persists_one_order_in_repository(
    order_create: CreateOrder,
    fake_order_repository: FakeOrderRepository,
) -> None:
    await order_create.execute(customer_name="Maria")
    assert len(fake_order_repository.created) == 1


@pytest.mark.asyncio
async def test_publishes_order_created(
    order_create: CreateOrder,
    fake_event_publisher: FakeEventPublisher,
) -> None:
    await order_create.execute(customer_name="Maria")
    assert fake_event_publisher.published == [
        (
            "order.created",
            {
                "id": 1,
                "customer_name": "Maria",
                "total": 0.0,
                "status": "PENDING",
            },
        )
    ]
