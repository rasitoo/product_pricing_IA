def test_channel_ingestion_contract(client):
    res = client.post(
        "/api/v1/channel-ingestion/normalize",
        json={"source_channel": "telegram", "photos": [{"filename": "x.jpg", "content_base64": "YQ=="}]},
    )
    assert res.status_code == 200
    assert res.json()["source_channel"] == "telegram"
