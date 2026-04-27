def test_health_returns_200(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok_json(client) -> None:
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
