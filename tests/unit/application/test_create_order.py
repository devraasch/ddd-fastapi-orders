import pytest

from app.application.use_cases.create_order import CreateOrderUseCase
from app.domain.value_objects.order_status import OrderStatus
from tests.mocks.fake_event_publisher import FakeEventPublisher
from tests.mocks.fake_order_repository import FakeOrderRepository


@pytest.mark.asyncio
async def test_create_order_use_case_yields_status_pending(
    create_order_use_case: CreateOrderUseCase,
) -> None:
    result = await create_order_use_case.execute(customer_name="Maria")
    assert result.status is OrderStatus.PENDING


@pytest.mark.asyncio
async def test_create_order_use_case_starts_with_zero_total(
    create_order_use_case: CreateOrderUseCase,
) -> None:
    result = await create_order_use_case.execute(customer_name="Maria")
    assert result.total == 0.0


@pytest.mark.asyncio
async def test_create_order_use_case_persists_one_order_in_repository(
    create_order_use_case: CreateOrderUseCase,
    fake_order_repository: FakeOrderRepository,
) -> None:
    await create_order_use_case.execute(customer_name="Maria")
    assert len(fake_order_repository.created) == 1


@pytest.mark.asyncio
async def test_create_order_use_case_publishes_order_created_event(
    create_order_use_case: CreateOrderUseCase,
    fake_event_publisher: FakeEventPublisher,
) -> None:
    await create_order_use_case.execute(customer_name="Maria")
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
