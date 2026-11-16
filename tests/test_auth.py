import pytest


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_register_new_user(client):
    res = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User",
        "org_name": "New Org"
    })
    assert res.status_code == 200, f"Register failed: {res.status_code} {res.text}"
    data = res.json()
    assert "access_token" in data


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "password": "pw",
        "full_name": "User",
        "org_name": "Org"
    })
    res = client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "password": "pw",
        "full_name": "User",
        "org_name": "Org"
    })
    assert res.status_code == 400


def test_login_valid(client):
    client.post("/api/auth/register", json={
        "email": "login@example.com",
        "password": "password",
        "full_name": "Login User",
        "org_name": "Login Org"
    })
    res = client.post("/api/auth/login", data={"username": "login@example.com", "password": "password"})
    assert res.status_code == 200, f"Login failed: {res.status_code} {res.text}"
    assert "access_token" in res.json()


def test_login_invalid(client):
    res = client.post("/api/auth/login", data={"username": "nope@example.com", "password": "wrong"})
    assert res.status_code == 401


def test_me_authenticated(client):
    reg = client.post("/api/auth/register", json={
        "email": "me@example.com",
        "password": "password123",
        "full_name": "Me User",
        "org_name": "Me Org"
    })
    assert reg.status_code == 200, f"Register failed: {reg.text}"
    token = reg.json()["access_token"]
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"Me failed: {res.text}"
    assert res.json()["email"] == "me@example.com"


def test_me_unauthenticated(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
