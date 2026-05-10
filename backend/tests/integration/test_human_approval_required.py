def test_human_approval_required(client):
    res = client.post("/api/v1/products/00000000-0000-0000-0000-000000000000/export")
    assert res.status_code == 412
