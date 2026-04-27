def test_post_orders_returns_status_code_200(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.post(
        "/orders",
        json={"customer_name": "Maria"},
    )
    assert response.status_code == 200


def test_post_orders_response_json_matches_expected_payload(order_client) -> None:
    client, _repo, _publisher = order_client
    response = client.post(
        "/orders",
        json={"customer_name": "Maria"},
    )
    assert response.json() == {
        "id": 1,
        "customer_name": "Maria",
        "total": 0.0,
        "status": "PENDING",
    }


def test_post_orders_records_single_order_created_event_in_fake_publisher(
    order_client,
) -> None:
    client, _repo, publisher = order_client
    client.post(
        "/orders",
        json={"customer_name": "Maria"},
    )
    assert publisher.published == [
        (
            "order.created",
            {
                "id": 1,
                "customer_name": "Maria",
                "total": 0.0,
                "status": "PENDING",
            },
        )
    ]
