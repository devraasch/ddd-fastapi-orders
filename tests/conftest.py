import pytest
from fastapi.testclient import TestClient

from app.application.use_cases.cancel_order import CancelOrder
from app.application.use_cases.confirm_order import ConfirmOrder
from app.application.use_cases.create_order import CreateOrder
from app.application.use_cases.get_order import GetOrder
from app.application.use_cases.list_orders import ListOrders
from app.main import create_app, noop_lifespan
from app.presentation.api.dependencies import (
    get_cancel_order as cancel_order_dep,
    get_confirm_order as confirm_order_dep,
    get_create_order as create_order_dep,
    get_list_orders as list_orders_dep,
    get_order as get_order_dep,
)
from tests.mocks.fake_event_publisher import FakeEventPublisher
from tests.mocks.fake_order_repository import FakeOrderRepository


@pytest.fixture
def app():
    return create_app(lifespan=noop_lifespan)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def order_client(app):
    repo = FakeOrderRepository()
    publisher = FakeEventPublisher()

    def override_create():
        return CreateOrder(
            order_repository=repo,
            event_publisher=publisher,
        )

    def override_get():
        return GetOrder(order_repository=repo)

    def override_list():
        return ListOrders(order_repository=repo)

    def override_confirm():
        return ConfirmOrder(
            order_repository=repo,
            event_publisher=publisher,
        )

    def override_cancel():
        return CancelOrder(
            order_repository=repo,
            event_publisher=publisher,
        )

    app.dependency_overrides[create_order_dep] = override_create
    app.dependency_overrides[get_order_dep] = override_get
    app.dependency_overrides[list_orders_dep] = override_list
    app.dependency_overrides[confirm_order_dep] = override_confirm
    app.dependency_overrides[cancel_order_dep] = override_cancel
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
def order_create(
    fake_order_repository: FakeOrderRepository,
    fake_event_publisher: FakeEventPublisher,
) -> CreateOrder:
    return CreateOrder(
        order_repository=fake_order_repository,
        event_publisher=fake_event_publisher,
    )


@pytest.fixture
def order_read(
    fake_order_repository: FakeOrderRepository,
) -> GetOrder:
    return GetOrder(order_repository=fake_order_repository)


@pytest.fixture
def order_list(
    fake_order_repository: FakeOrderRepository,
) -> ListOrders:
    return ListOrders(order_repository=fake_order_repository)


@pytest.fixture
def order_confirm(
    fake_order_repository: FakeOrderRepository,
    fake_event_publisher: FakeEventPublisher,
) -> ConfirmOrder:
    return ConfirmOrder(
        order_repository=fake_order_repository,
        event_publisher=fake_event_publisher,
    )


@pytest.fixture
def order_cancel(
    fake_order_repository: FakeOrderRepository,
    fake_event_publisher: FakeEventPublisher,
) -> CancelOrder:
    return CancelOrder(
        order_repository=fake_order_repository,
        event_publisher=fake_event_publisher,
    )
