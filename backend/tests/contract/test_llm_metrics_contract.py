def test_llm_metrics_contract(client):
    res = client.get("/api/v1/metrics/llm")
    assert res.status_code == 200
    body = res.json()
    assert "total_calls" in body
    assert "total_cost_usd" in body
