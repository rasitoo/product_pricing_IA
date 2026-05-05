def test_review_proposal_not_found(client):
    res = client.post(
        "/api/v1/proposals/00000000-0000-0000-0000-000000000000/review",
        json={"decision": "approve", "operator_id": "ops-1"},
    )
    assert res.status_code == 404
