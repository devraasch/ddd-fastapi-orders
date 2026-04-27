def test_post_orders_returns_200(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.post(
        "/orders",
        json={
            "customer_name": "Maria",
            "items": [{"product_id": 1, "quantity": 1, "unit_price": 0.0}],
        },
    )
    assert response.status_code == 200


def test_post_orders_response_shape(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.post(
        "/orders",
        json={
            "customer_name": "Maria",
            "items": [
                {"product_id": 1, "quantity": 2, "unit_price": 4.0},
                {"product_id": 2, "quantity": 1, "unit_price": 1.0},
            ],
        },
    )
    assert response.json() == {
        "id": 1,
        "customer_name": "Maria",
        "total": 9.0,
        "status": "PENDING",
        "items": [
            {"product_id": 1, "quantity": 2, "unit_price": 4.0},
            {"product_id": 2, "quantity": 1, "unit_price": 1.0},
        ],
    }


def test_post_orders_publishes_created_event(order_client) -> None:
    client, _repo, publisher = order_client
    client.post(
        "/orders",
        json={
            "customer_name": "Maria",
            "items": [{"product_id": 7, "quantity": 1, "unit_price": 3.0}],
        },
    )
    assert publisher.published == [
        (
            "order.created",
            {
                "id": 1,
                "customer_name": "Maria",
                "total": 3.0,
                "status": "PENDING",
            },
        )
    ]


def test_post_orders_rejects_empty_items_422(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.post(
        "/orders",
        json={"customer_name": "Maria", "items": []},
    )
    assert response.status_code == 422
