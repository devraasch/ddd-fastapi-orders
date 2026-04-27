import pytest

from app.domain.entities.order import Order
from app.domain.entities.order_item import OrderItem
from app.domain.exceptions import InvalidOrderItemError, OrderMutationNotAllowed
from app.domain.value_objects.order_status import OrderStatus


def test_new_order_starts_as_pending() -> None:
    order = Order(id=None, customer_name="Alice")
    assert order.status is OrderStatus.PENDING


def test_new_order_total_is_zero_without_items() -> None:
    order = Order(id=None, customer_name="Alice")
    assert order.total == 0.0


def test_total_is_sum_of_line_totals() -> None:
    order = Order(id=None, customer_name="Alice")
    order.add_item(product_id=1, quantity=2, unit_price=5.0)
    order.add_item(product_id=2, quantity=1, unit_price=3.0)
    assert order.total == 13.0


def test_line_total_is_quantity_times_unit_price() -> None:
    line = OrderItem(product_id=1, quantity=3, unit_price=4.0)
    assert line.line_total == 12.0


def test_order_item_allows_zero_unit_price() -> None:
    line = OrderItem(product_id=1, quantity=1, unit_price=0.0)
    assert line.line_total == 0.0


def test_order_item_rejects_zero_quantity() -> None:
    with pytest.raises(InvalidOrderItemError):
        OrderItem(product_id=1, quantity=0, unit_price=1.0)


def test_order_item_rejects_negative_unit_price() -> None:
    with pytest.raises(InvalidOrderItemError):
        OrderItem(product_id=1, quantity=1, unit_price=-0.01)


def test_add_item_increments_total() -> None:
    order = Order(id=None, customer_name="Alice")
    order.add_item(product_id=1, quantity=1, unit_price=10.0)
    assert order.total == 10.0


def test_remove_item_clears_total_when_last_line_removed() -> None:
    order = Order(id=None, customer_name="Alice")
    order.add_item(product_id=7, quantity=1, unit_price=5.0)
    order.remove_item(product_id=7)
    assert order.total == 0.0


def test_cannot_add_item_when_order_is_confirmed() -> None:
    order = Order(
        id=1,
        customer_name="Bob",
        status=OrderStatus.CONFIRMED,
        items=[],
    )
    with pytest.raises(OrderMutationNotAllowed):
        order.add_item(product_id=1, quantity=1, unit_price=1.0)


def test_cannot_add_item_when_order_is_cancelled() -> None:
    order = Order(
        id=1,
        customer_name="Bob",
        status=OrderStatus.CANCELLED,
        items=[],
    )
    with pytest.raises(OrderMutationNotAllowed):
        order.add_item(product_id=1, quantity=1, unit_price=1.0)


def test_cannot_remove_item_when_order_is_confirmed() -> None:
    order = Order(
        id=1,
        customer_name="Bob",
        status=OrderStatus.CONFIRMED,
        items=[],
    )
    with pytest.raises(OrderMutationNotAllowed):
        order.remove_item(product_id=1)


def test_cannot_remove_item_when_order_is_cancelled() -> None:
    order = Order(
        id=1,
        customer_name="Bob",
        status=OrderStatus.CANCELLED,
        items=[],
    )
    with pytest.raises(OrderMutationNotAllowed):
        order.remove_item(product_id=1)


def test_order_stores_customer_name() -> None:
    order = Order(id=None, customer_name="Alice")
    assert order.customer_name == "Alice"


def test_order_allows_id_none_before_persistence() -> None:
    order = Order(id=None, customer_name="Alice")
    assert order.id is None
