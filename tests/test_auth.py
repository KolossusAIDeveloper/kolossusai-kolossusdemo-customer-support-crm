import pytest


def test_register_new_user(client):
    res = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User",
        "org_name": "New Org"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


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
        "full_name": "Login User"
    })
    res = client.post("/api/auth/login", data={"username": "login@example.com", "password": "password"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_invalid(client):
    res = client.post("/api/auth/login", data={"username": "nope@example.com", "password": "wrong"})
    assert res.status_code == 401


def test_me_authenticated(client, auth_headers):
    headers, _ = auth_headers
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"


def test_me_unauthenticated(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
