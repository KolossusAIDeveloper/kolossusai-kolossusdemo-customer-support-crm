import pytest


def test_create_deal(client, auth_headers):
    headers, org_id = auth_headers
    res = client.post(f"/api/deals?org_id={org_id}", json={
        "name": "Big Contract",
        "value": 50000,
        "stage": "new"
    }, headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Big Contract"
    assert res.json()["value"] == 50000.0


def test_list_deals(client, auth_headers):
    headers, org_id = auth_headers
    res = client.get(f"/api/deals?org_id={org_id}", headers=headers)
    assert res.status_code == 200
    assert "items" in res.json()


def test_move_deal_stage(client, auth_headers):
    headers, org_id = auth_headers
    create_res = client.post(f"/api/deals?org_id={org_id}", json={"name": "Stage Test", "value": 1000}, headers=headers)
    deal_id = create_res.json()["id"]
    res = client.post(f"/api/deals/{deal_id}/move-stage?org_id={org_id}", json={"stage": "qualified"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["stage"] == "qualified"


def test_move_deal_to_won(client, auth_headers):
    headers, org_id = auth_headers
    create_res = client.post(f"/api/deals?org_id={org_id}", json={"name": "Won Deal", "value": 25000}, headers=headers)
    deal_id = create_res.json()["id"]
    res = client.post(f"/api/deals/{deal_id}/move-stage?org_id={org_id}", json={"stage": "won"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["stage"] == "won"


def test_move_deal_to_lost_with_reason(client, auth_headers):
    headers, org_id = auth_headers
    create_res = client.post(f"/api/deals?org_id={org_id}", json={"name": "Lost Deal", "value": 5000}, headers=headers)
    deal_id = create_res.json()["id"]
    res = client.post(f"/api/deals/{deal_id}/move-stage?org_id={org_id}", json={"stage": "lost", "lost_reason": "Budget"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["stage"] == "lost"
    assert res.json()["lost_reason"] == "Budget"


def test_analytics_dashboard(client, auth_headers):
    headers, org_id = auth_headers
    res = client.get(f"/api/analytics/dashboard?org_id={org_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_leads" in data
    assert "pipeline_value" in data
    assert "won_deals" in data
