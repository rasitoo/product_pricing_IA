def test_export_requires_approval(client):
    res = client.post("/api/v1/products/00000000-0000-0000-0000-000000000000/export")
    assert res.status_code == 412
