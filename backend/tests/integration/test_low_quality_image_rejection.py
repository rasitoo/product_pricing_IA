def test_low_quality_image_rejection(client):
    payload = {"source_channel": "api", "photos": []}
    res = client.post("/api/v1/products", json=payload)
    assert res.status_code == 422
