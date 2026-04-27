from app.domain.entities.order import Order


def test_order_allows_id_none_before_persistence() -> None:
    order = Order(id=None, customer_name="Alice", total=1.0)
    assert order.id is None


def test_order_stores_customer_name() -> None:
    order = Order(id=None, customer_name="Alice", total=1.0)
    assert order.customer_name == "Alice"


def test_order_stores_total() -> None:
    order = Order(id=None, customer_name="Alice", total=42.5)
    assert order.total == 42.5


def test_order_uses_pending_status_by_default() -> None:
    order = Order(id=None, customer_name="Alice", total=1.0)
    assert order.status == "PENDING"


def test_order_accepts_non_default_status() -> None:
    order = Order(
        id=1,
        customer_name="Bob",
        total=10.0,
        status="CONFIRMED",
    )
    assert order.status == "CONFIRMED"
