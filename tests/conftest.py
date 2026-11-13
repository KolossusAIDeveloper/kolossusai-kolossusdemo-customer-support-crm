import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
        "org_name": "Test Org"
    })
    res = client.post("/api/auth/login", data={"username": "test@example.com", "password": "testpassword"})
    token = res.json()["access_token"]
    orgs = client.get("/api/auth/organizations", headers={"Authorization": f"Bearer {token}"})
    org_id = orgs.json()[0]["id"] if orgs.json() else None
    return {"Authorization": f"Bearer {token}"}, org_id
