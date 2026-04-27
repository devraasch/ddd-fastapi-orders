def test_health_get_returns_status_code_200(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_health_get_returns_json_body_status_ok(client) -> None:
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
