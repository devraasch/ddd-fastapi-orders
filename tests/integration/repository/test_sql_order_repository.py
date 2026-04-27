import pytest

from app.domain.entities.order import Order
from app.domain.value_objects.order_status import OrderStatus
from app.infrastructure.repositories.sql_order_repository import SqlOrderRepository

pytestmark = [pytest.mark.integration_db]


async def _create_order_with_two_lines(
    sql_order_repository: SqlOrderRepository,
) -> int:
    order = Order(id=None, customer_name="Eve")
    order.add_item(product_id=10, quantity=2, unit_price=5.0)
    order.add_item(product_id=20, quantity=1, unit_price=3.0)
    created = await sql_order_repository.create(order)
    return created.id


@pytest.mark.asyncio
async def test_create_returns_order_with_items_total(
    sql_order_repository: SqlOrderRepository,
) -> None:
    order = Order(id=None, customer_name="Eve")
    order.add_item(product_id=10, quantity=2, unit_price=5.0)
    order.add_item(product_id=20, quantity=1, unit_price=3.0)
    created = await sql_order_repository.create(order)
    assert created.total == 13.0


@pytest.mark.asyncio
async def test_get_by_id_reloads_status_pending(
    sql_order_repository: SqlOrderRepository,
) -> None:
    order_id = await _create_order_with_two_lines(sql_order_repository)
    loaded = await sql_order_repository.get_by_id(order_id)
    assert loaded.status is OrderStatus.PENDING


@pytest.mark.asyncio
async def test_get_by_id_reloads_customer_name(
    sql_order_repository: SqlOrderRepository,
) -> None:
    order_id = await _create_order_with_two_lines(sql_order_repository)
    loaded = await sql_order_repository.get_by_id(order_id)
    assert loaded.customer_name == "Eve"


@pytest.mark.asyncio
async def test_get_by_id_reloads_item_count(
    sql_order_repository: SqlOrderRepository,
) -> None:
    order_id = await _create_order_with_two_lines(sql_order_repository)
    loaded = await sql_order_repository.get_by_id(order_id)
    assert len(loaded.items) == 2


@pytest.mark.asyncio
async def test_get_by_id_reloads_first_line_product(
    sql_order_repository: SqlOrderRepository,
) -> None:
    order_id = await _create_order_with_two_lines(sql_order_repository)
    loaded = await sql_order_repository.get_by_id(order_id)
    assert loaded.items[0].product_id == 10


@pytest.mark.asyncio
async def test_get_by_id_reloads_total_from_database(
    sql_order_repository: SqlOrderRepository,
) -> None:
    order_id = await _create_order_with_two_lines(sql_order_repository)
    loaded = await sql_order_repository.get_by_id(order_id)
    assert loaded.total == 13.0


@pytest.mark.asyncio
async def test_get_by_id_missing_returns_none(
    sql_order_repository: SqlOrderRepository,
) -> None:
    missing = await sql_order_repository.get_by_id(9_999_999)
    assert missing is None
