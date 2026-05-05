import base64


def test_product_analysis_flow(client):
    payload = {
        "source_channel": "api",
        "photos": [{"filename": "c.jpg", "content_base64": base64.b64encode(b"ghi").decode()}],
    }
    res = client.post("/api/v1/products", json=payload)
    assert res.status_code == 202
