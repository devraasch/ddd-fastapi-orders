import asyncio


def test_confirm_unknown_order_404(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.post("/orders/404/confirm")
    assert response.status_code == 404


def test_confirm_empty_cart_400(order_client) -> None:
    client, _repo, _publisher = order_client
    client.post("/orders", json={"customer_name": "X"})
    response = client.post("/orders/1/confirm")
    assert response.status_code == 400


def _add_one_line_to_order_1(repo) -> None:
    async def go() -> None:
        o = await repo.get_by_id(1)
        o.add_item(product_id=1, quantity=1, unit_price=2.0)

    asyncio.run(go())


def test_confirm_with_line_ok(order_client) -> None:
    client, repo, _publisher = order_client
    client.post("/orders", json={"customer_name": "Y"})
    _add_one_line_to_order_1(repo)
    response = client.post("/orders/1/confirm")
    assert response.status_code == 200


def test_confirm_response_status_confirmed(order_client) -> None:
    client, repo, _publisher = order_client
    client.post("/orders", json={"customer_name": "Y"})
    _add_one_line_to_order_1(repo)
    response = client.post("/orders/1/confirm")
    assert response.json()["status"] == "CONFIRMED"


def test_cancel_pending_ok(order_client) -> None:
    client, _repo, _publisher = order_client
    client.post("/orders", json={"customer_name": "Z"})
    response = client.post("/orders/1/cancel")
    assert response.status_code == 200


def test_cancel_twice_400(order_client) -> None:
    client, _repo, _publisher = order_client
    client.post("/orders", json={"customer_name": "Z"})
    client.post("/orders/1/cancel")
    response = client.post("/orders/1/cancel")
    assert response.status_code == 400


def test_cancel_unknown_404(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.post("/orders/999/cancel")
    assert response.status_code == 404


def test_cancel_publishes_cancelled_event(order_client) -> None:
    client, _repo, publisher = order_client
    client.post("/orders", json={"customer_name": "Z"})
    client.post("/orders/1/cancel")
    assert publisher.published[-1][0] == "order.cancelled"
