import base64


def test_get_proposal_contract(client):
    payload = {
        "source_channel": "api",
        "photos": [{"filename": "b.jpg", "content_base64": base64.b64encode(b"def").decode()}],
    }
    create = client.post("/api/v1/products", json=payload)
    assert create.status_code == 202

    metrics = client.get("/api/v1/metrics/llm")
    assert metrics.status_code == 200
