import asyncio

from app.domain.entities.order import Order

_LINE = {"product_id": 1, "quantity": 1, "unit_price": 0.0}
_POST = {"customer_name": "Maria", "items": [_LINE]}


def test_read_order_returns_200_after_post(order_client) -> None:
    client, _repo, _publisher = order_client
    client.post("/orders", json=_POST)
    response = client.get("/orders/1")
    assert response.status_code == 200


def test_read_order_includes_posted_items(order_client) -> None:
    client, _repo, _publisher = order_client
    client.post(
        "/orders",
        json={
            "customer_name": "Maria",
            "items": [
                {"product_id": 10, "quantity": 1, "unit_price": 2.0},
            ],
        },
    )
    response = client.get("/orders/1")
    assert response.json()["items"] == [
        {"product_id": 10, "quantity": 1, "unit_price": 2.0},
    ]


def test_read_order_unknown_returns_404(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.get("/orders/9999")
    assert response.status_code == 404


def test_list_orders_empty_initially(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.get("/orders")
    assert response.json() == []


def test_list_orders_shows_created_order(order_client) -> None:
    client, _repo, _publisher = order_client
    client.post(
        "/orders",
        json={
            "customer_name": "Maria",
            "items": [
                {"product_id": 1, "quantity": 1, "unit_price": 0.0},
            ],
        },
    )
    response = client.get("/orders")
    assert response.json() == [
        {
            "id": 1,
            "customer_name": "Maria",
            "total": 0.0,
            "status": "PENDING",
            "items": [
                {"product_id": 1, "quantity": 1, "unit_price": 0.0},
            ],
        }
    ]


def test_read_order_total_from_seeded_lines(order_client) -> None:
    client, repo, _publisher = order_client

    async def seed() -> None:
        o = Order(id=None, customer_name="Ana")
        o.add_item(product_id=5, quantity=2, unit_price=3.0)
        await repo.create(o)

    asyncio.run(seed())
    response = client.get("/orders/1")
    assert response.json()["total"] == 6.0
