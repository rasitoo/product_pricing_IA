def test_additional_channel_ingestion(client):
    res = client.post(
        "/api/v1/channel-ingestion/normalize",
        json={"source_channel": "whatsapp", "photos": [{"filename": "x.jpg", "content_base64": "YQ=="}]},
    )
    assert res.status_code == 200
    assert res.json()["source_channel"] == "whatsapp"
