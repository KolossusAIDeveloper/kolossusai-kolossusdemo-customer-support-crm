import pytest


def test_create_lead(client, auth_headers):
    headers, org_id = auth_headers
    res = client.post(f"/api/leads?org_id={org_id}", json={
        "name": "John Doe",
        "email": "john@example.com",
        "company": "Acme"
    }, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "John Doe"
    assert data["organization_id"] == org_id


def test_create_duplicate_lead_email(client, auth_headers):
    headers, org_id = auth_headers
    client.post(f"/api/leads?org_id={org_id}", json={"name": "Lead A", "email": "dup@lead.com"}, headers=headers)
    res = client.post(f"/api/leads?org_id={org_id}", json={"name": "Lead B", "email": "dup@lead.com"}, headers=headers)
    assert res.status_code == 409


def test_list_leads(client, auth_headers):
    headers, org_id = auth_headers
    res = client.get(f"/api/leads?org_id={org_id}", headers=headers)
    assert res.status_code == 200
    assert "items" in res.json()


def test_update_lead(client, auth_headers):
    headers, org_id = auth_headers
    create_res = client.post(f"/api/leads?org_id={org_id}", json={"name": "Update Me", "email": "updateme@test.com"}, headers=headers)
    lead_id = create_res.json()["id"]
    res = client.patch(f"/api/leads/{lead_id}?org_id={org_id}", json={"status": "qualified"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "qualified"


def test_delete_lead(client, auth_headers):
    headers, org_id = auth_headers
    create_res = client.post(f"/api/leads?org_id={org_id}", json={"name": "Delete Me", "email": "deleteme@test.com"}, headers=headers)
    lead_id = create_res.json()["id"]
    res = client.delete(f"/api/leads/{lead_id}?org_id={org_id}", headers=headers)
    assert res.status_code == 200
    get_res = client.get(f"/api/leads/{lead_id}?org_id={org_id}", headers=headers)
    assert get_res.status_code == 404


def test_org_isolation(client):
    # Register two separate orgs and verify they can't see each other's leads
    r1 = client.post("/api/auth/register", json={"email": "org1@test.com", "password": "pw", "full_name": "O1", "org_name": "Org1"})
    r2 = client.post("/api/auth/register", json={"email": "org2@test.com", "password": "pw", "full_name": "O2", "org_name": "Org2"})

    t1 = r1.json()["access_token"]
    t2 = r2.json()["access_token"]

    orgs1 = client.get("/api/auth/organizations", headers={"Authorization": f"Bearer {t1}"}).json()
    orgs2 = client.get("/api/auth/organizations", headers={"Authorization": f"Bearer {t2}"}).json()

    org1_id = orgs1[0]["id"]
    org2_id = orgs2[0]["id"]

    client.post(f"/api/leads?org_id={org1_id}", json={"name": "Org1 Lead"}, headers={"Authorization": f"Bearer {t1}"})

    # Org2 should not see org1's lead
    res = client.get(f"/api/leads?org_id={org2_id}", headers={"Authorization": f"Bearer {t2}"})
    assert res.status_code == 200
    for lead in res.json()["items"]:
        assert lead["organization_id"] == org2_id
