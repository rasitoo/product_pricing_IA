def test_concurrent_review_conflict_placeholder(client):
    # Placeholder until optimistic locking is implemented.
    res = client.post(
        "/api/v1/proposals/00000000-0000-0000-0000-000000000000/review",
        json={"decision": "approve", "operator_id": "ops-1"},
    )
    assert res.status_code in (404, 409)
