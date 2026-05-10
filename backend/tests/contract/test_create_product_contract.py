import base64


def test_create_product_contract(client):
    payload = {
        "source_channel": "api",
        "photos": [{"filename": "a.jpg", "content_base64": base64.b64encode(b"abc").decode()}],
    }
    res = client.post("/api/v1/products", json=payload)
    assert res.status_code == 202
    body = res.json()
    assert "product_id" in body
    assert body["status"] == "analyzing"
