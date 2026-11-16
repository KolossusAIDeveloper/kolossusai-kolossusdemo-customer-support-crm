import pytest


def _register_and_login(client, email="lead_user@example.com"):
    reg = client.post("/api/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Test User",
        "org_name": "Test Org"
    })
    assert reg.status_code == 200, f"Register failed: {reg.text}"
    data = reg.json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data.get("org_id")


def test_create_lead(client):
    headers, org_id = _register_and_login(client)
    res = client.post(f"/api/leads?org_id={org_id}", json={
        "name": "John Doe",
        "email": "john@example.com",
        "company": "Acme"
    }, headers=headers)
    assert res.status_code == 200, f"Create lead failed: {res.text}"
    data = res.json()
    assert data["name"] == "John Doe"
    assert data["organization_id"] == org_id


def test_create_duplicate_lead_email(client):
    headers, org_id = _register_and_login(client)
    client.post(f"/api/leads?org_id={org_id}", json={"name": "Lead A", "email": "dup@lead.com"}, headers=headers)
    res = client.post(f"/api/leads?org_id={org_id}", json={"name": "Lead B", "email": "dup@lead.com"}, headers=headers)
    assert res.status_code == 409


def test_list_leads(client):
    headers, org_id = _register_and_login(client)
    res = client.get(f"/api/leads?org_id={org_id}", headers=headers)
    assert res.status_code == 200
    assert "items" in res.json()


def test_update_lead(client):
    headers, org_id = _register_and_login(client)
    create_res = client.post(f"/api/leads?org_id={org_id}", json={"name": "Update Me", "email": "updateme@test.com"}, headers=headers)
    assert create_res.status_code == 200, f"Create failed: {create_res.text}"
    lead_id = create_res.json()["id"]
    res = client.patch(f"/api/leads/{lead_id}?org_id={org_id}", json={"status": "qualified"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "qualified"


def test_delete_lead(client):
    headers, org_id = _register_and_login(client)
    create_res = client.post(f"/api/leads?org_id={org_id}", json={"name": "Delete Me", "email": "deleteme@test.com"}, headers=headers)
    assert create_res.status_code == 200
    lead_id = create_res.json()["id"]
    res = client.delete(f"/api/leads/{lead_id}?org_id={org_id}", headers=headers)
    assert res.status_code == 200
    get_res = client.get(f"/api/leads/{lead_id}?org_id={org_id}", headers=headers)
    assert get_res.status_code == 404


def test_org_isolation(client):
    r1 = client.post("/api/auth/register", json={"email": "org1@test.com", "password": "pw", "full_name": "O1", "org_name": "Org1"})
    r2 = client.post("/api/auth/register", json={"email": "org2@test.com", "password": "pw", "full_name": "O2", "org_name": "Org2"})
    assert r1.status_code == 200
    assert r2.status_code == 200

    t1 = r1.json()["access_token"]
    t2 = r2.json()["access_token"]
    org1_id = r1.json().get("org_id")
    org2_id = r2.json().get("org_id")

    client.post(f"/api/leads?org_id={org1_id}", json={"name": "Org1 Lead"}, headers={"Authorization": f"Bearer {t1}"})

    res = client.get(f"/api/leads?org_id={org2_id}", headers={"Authorization": f"Bearer {t2}"})
    assert res.status_code == 200
    for lead in res.json()["items"]:
        assert lead["organization_id"] == org2_id
