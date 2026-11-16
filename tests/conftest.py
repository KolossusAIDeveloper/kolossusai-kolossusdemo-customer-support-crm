import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "testsecretkey123changeme")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ["PYTEST_CURRENT_TEST"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
        "org_name": "Test Org"
    })
    res = client.post("/api/auth/login", data={"username": "test@example.com", "password": "testpassword"})
    data = res.json()
    token = data.get("access_token", "")
    org_id = data.get("org_id", None)
    return {"Authorization": f"Bearer {token}"}, org_id
