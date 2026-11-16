#!/usr/bin/env python3
import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "testsecretkey123changeme"
os.environ["AI_PROVIDER"] = "mock"
os.environ["PYTEST_CURRENT_TEST"] = "1"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

try:
    from app.main import app
    print("App imported OK")
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base, get_db

    engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    # Test health
    res = client.get("/api/health")
    print(f"Health: {res.status_code} {res.json()}")

    # Test register
    res = client.post("/api/auth/register", json={
        "email": "test@test.com",
        "password": "password123",
        "full_name": "Test User",
        "org_name": "Test Org"
    })
    print(f"Register: {res.status_code} {res.text[:200]}")

except Exception as e:
    import traceback
    print("ERROR:")
    traceback.print_exc()
