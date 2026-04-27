import pytest
from fastapi.testclient import TestClient

from app.application.use_cases.create_order import CreateOrderUseCase
from app.main import create_app, noop_lifespan
from app.presentation.api.dependencies import get_create_order_use_case
from tests.mocks.fake_event_publisher import FakeEventPublisher
from tests.mocks.fake_order_repository import FakeOrderRepository


@pytest.fixture
def app():
    """App sem startup de Postgres/RabbitMQ."""
    return create_app(lifespan=noop_lifespan)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def order_client(app):
    """Cliente HTTP com caso de uso substituído por fakes (sem I/O real)."""
    repo = FakeOrderRepository()
    publisher = FakeEventPublisher()

    def override_create_order_use_case() -> CreateOrderUseCase:
        return CreateOrderUseCase(
            order_repository=repo,
            event_publisher=publisher,
        )

    app.dependency_overrides[get_create_order_use_case] = override_create_order_use_case
    with TestClient(app) as c:
        yield c, repo, publisher
    app.dependency_overrides.clear()


@pytest.fixture
def fake_order_repository() -> FakeOrderRepository:
    return FakeOrderRepository()


@pytest.fixture
def fake_event_publisher() -> FakeEventPublisher:
    return FakeEventPublisher()


@pytest.fixture
def create_order_use_case(
    fake_order_repository: FakeOrderRepository,
    fake_event_publisher: FakeEventPublisher,
) -> CreateOrderUseCase:
    """Caso de uso com fakes — sem Postgres nem RabbitMQ."""
    return CreateOrderUseCase(
        order_repository=fake_order_repository,
        event_publisher=fake_event_publisher,
    )
