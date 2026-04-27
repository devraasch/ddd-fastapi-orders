import pytest

from app.application.use_cases.create_order import CreateOrderUseCase
from tests.mocks.fake_event_publisher import FakeEventPublisher
from tests.mocks.fake_order_repository import FakeOrderRepository


@pytest.mark.asyncio
async def test_create_order_use_case_yields_status_pending(
    create_order_use_case: CreateOrderUseCase,
) -> None:
    result = await create_order_use_case.execute(
        customer_name="Maria",
        total=150.0,
    )
    assert result.status == "PENDING"


@pytest.mark.asyncio
async def test_create_order_use_case_persists_one_order_in_repository(
    create_order_use_case: CreateOrderUseCase,
    fake_order_repository: FakeOrderRepository,
) -> None:
    await create_order_use_case.execute(
        customer_name="Maria",
        total=150.0,
    )
    assert len(fake_order_repository.created) == 1


@pytest.mark.asyncio
async def test_create_order_use_case_publishes_order_created_event(
    create_order_use_case: CreateOrderUseCase,
    fake_event_publisher: FakeEventPublisher,
) -> None:
    await create_order_use_case.execute(
        customer_name="Maria",
        total=150.0,
    )
    assert fake_event_publisher.published == [
        (
            "order.created",
            {
                "id": 1,
                "customer_name": "Maria",
                "total": 150.0,
                "status": "PENDING",
            },
        )
    ]
