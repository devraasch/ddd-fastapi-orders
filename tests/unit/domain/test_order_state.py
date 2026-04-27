import pytest

from app.domain.entities.order import Order
from app.domain.entities.order_item import OrderItem
from app.domain.exceptions import CannotCancelOrderError, CannotConfirmOrderError
from app.domain.value_objects.order_status import OrderStatus


def test_confirm_sets_status_confirmed() -> None:
    order = Order(id=1, customer_name="A")
    order.add_item(product_id=1, quantity=1, unit_price=1.0)
    order.confirm()
    assert order.status is OrderStatus.CONFIRMED


def test_confirm_rejects_empty_order() -> None:
    order = Order(id=1, customer_name="A")
    with pytest.raises(CannotConfirmOrderError):
        order.confirm()


def test_confirm_rejects_cancelled_order() -> None:
    order = Order(id=1, customer_name="A", status=OrderStatus.CANCELLED)
    with pytest.raises(CannotConfirmOrderError):
        order.confirm()


def test_confirm_rejects_already_confirmed() -> None:
    order = Order(
        id=1,
        customer_name="A",
        status=OrderStatus.CONFIRMED,
        items=[OrderItem(product_id=1, quantity=1, unit_price=1.0)],
    )
    with pytest.raises(CannotConfirmOrderError):
        order.confirm()


def test_cancel_from_pending_sets_cancelled() -> None:
    order = Order(id=1, customer_name="A")
    order.cancel()
    assert order.status is OrderStatus.CANCELLED


def test_cancel_from_confirmed_sets_cancelled() -> None:
    order = Order(id=1, customer_name="A", status=OrderStatus.CONFIRMED)
    order.cancel()
    assert order.status is OrderStatus.CANCELLED


def test_cancel_rejects_double_cancel() -> None:
    order = Order(id=1, customer_name="A", status=OrderStatus.CANCELLED)
    with pytest.raises(CannotCancelOrderError):
        order.cancel()
