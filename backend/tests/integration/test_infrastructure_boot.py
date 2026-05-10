def test_health_boot(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
