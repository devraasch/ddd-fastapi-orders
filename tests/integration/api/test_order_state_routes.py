import asyncio

from app.domain.entities.order import Order

_POST_ONE_LINE = {
    "customer_name": "Y",
    "items": [{"product_id": 1, "quantity": 1, "unit_price": 2.0}],
}


def test_confirm_unknown_order_404(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.post("/orders/404/confirm")
    assert response.status_code == 404


def test_confirm_empty_order_400(order_client) -> None:
    client, repo, _publisher = order_client

    async def seed() -> None:
        await repo.create(Order(id=None, customer_name="X"))

    asyncio.run(seed())
    response = client.post("/orders/1/confirm")
    assert response.status_code == 400


def test_confirm_with_line_ok(order_client) -> None:
    client, _repo, _publisher = order_client
    client.post("/orders", json=_POST_ONE_LINE)
    response = client.post("/orders/1/confirm")
    assert response.status_code == 200


def test_confirm_response_status_confirmed(order_client) -> None:
    client, _repo, _publisher = order_client
    client.post("/orders", json=_POST_ONE_LINE)
    response = client.post("/orders/1/confirm")
    assert response.json()["status"] == "CONFIRMED"


def test_cancel_pending_ok(order_client) -> None:
    client, _repo, _publisher = order_client
    client.post(
        "/orders",
        json={
            "customer_name": "Z",
            "items": [{"product_id": 1, "quantity": 1, "unit_price": 0.0}],
        },
    )
    response = client.post("/orders/1/cancel")
    assert response.status_code == 200


def test_cancel_twice_400(order_client) -> None:
    client, _repo, _publisher = order_client
    client.post(
        "/orders",
        json={
            "customer_name": "Z",
            "items": [{"product_id": 1, "quantity": 1, "unit_price": 0.0}],
        },
    )
    client.post("/orders/1/cancel")
    response = client.post("/orders/1/cancel")
    assert response.status_code == 400


def test_cancel_unknown_404(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.post("/orders/999/cancel")
    assert response.status_code == 404


def test_cancel_publishes_cancelled_event(order_client) -> None:
    client, _repo, publisher = order_client
    client.post(
        "/orders",
        json={
            "customer_name": "Z",
            "items": [{"product_id": 1, "quantity": 1, "unit_price": 0.0}],
        },
    )
    client.post("/orders/1/cancel")
    assert publisher.published[-1][0] == "order.cancelled"
