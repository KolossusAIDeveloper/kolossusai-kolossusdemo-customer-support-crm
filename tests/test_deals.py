import pytest


def _register_and_login(client, email="deal_user@example.com"):
    reg = client.post("/api/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Test User",
        "org_name": "Test Org"
    })
    assert reg.status_code == 200, f"Register failed: {reg.text}"
    data = reg.json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data.get("org_id")


def test_create_deal(client):
    headers, org_id = _register_and_login(client)
    res = client.post(f"/api/deals?org_id={org_id}", json={
        "name": "Big Contract",
        "value": 50000,
        "stage": "new"
    }, headers=headers)
    assert res.status_code == 200, f"Create deal failed: {res.text}"
    assert res.json()["name"] == "Big Contract"
    assert res.json()["value"] == 50000.0


def test_list_deals(client):
    headers, org_id = _register_and_login(client)
    res = client.get(f"/api/deals?org_id={org_id}", headers=headers)
    assert res.status_code == 200
    assert "items" in res.json()


def test_move_deal_stage(client):
    headers, org_id = _register_and_login(client)
    create_res = client.post(f"/api/deals?org_id={org_id}", json={"name": "Stage Test", "value": 1000}, headers=headers)
    assert create_res.status_code == 200, f"Create deal failed: {create_res.text}"
    deal_id = create_res.json()["id"]
    res = client.post(f"/api/deals/{deal_id}/move-stage?org_id={org_id}", json={"stage": "qualified"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["stage"] == "qualified"


def test_move_deal_to_won(client):
    headers, org_id = _register_and_login(client)
    create_res = client.post(f"/api/deals?org_id={org_id}", json={"name": "Won Deal", "value": 25000}, headers=headers)
    assert create_res.status_code == 200
    deal_id = create_res.json()["id"]
    res = client.post(f"/api/deals/{deal_id}/move-stage?org_id={org_id}", json={"stage": "won"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["stage"] == "won"


def test_analytics_dashboard(client):
    headers, org_id = _register_and_login(client)
    res = client.get(f"/api/analytics/dashboard?org_id={org_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_leads" in data
    assert "pipeline_value" in data
    assert "won_deals" in data
