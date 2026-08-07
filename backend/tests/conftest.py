"""
Test configuration.

Uses an in-memory SQLite database instead of PostgreSQL so tests run
anywhere with no external services. Note: a handful of endpoints use
PostgreSQL-specific SQL (func.date_trunc for sales/revenue trend charts)
and won't work against SQLite — those are intentionally NOT covered by the
integration tests here. The pure AI service functions (forecasting,
anomaly detection, health scoring math, recommender, NLG) have no DB
dependency at all and are unit-tested directly instead, which also gives
better coverage of the actual logic than an integration test would.
"""
import os
os.environ["ENV"] = "test"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
import app.models  # noqa: F401 — ensure all models are registered on Base.metadata

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    from app.models.user import Role, Region, Permission

    for name in ["admin", "regional_manager", "outlet_manager"]:
        if not db.query(Role).filter(Role.name == name).first():
            db.add(Role(name=name, description=name))

    for name in ["North", "South", "East", "West"]:
        if not db.query(Region).filter(Region.name == name).first():
            db.add(Region(name=name, description=f"{name} region"))

    for code in ["outlets.read", "outlets.write", "users.manage", "reports.generate",
                 "recommendations.refresh", "audits.manage", "data.import"]:
        if not db.query(Permission).filter(Permission.code == code).first():
            db.add(Permission(code=code, description=code))

    db.commit()

    # Give admin every permission, mirroring schema.sql's seed logic.
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    admin_role.permissions = db.query(Permission).all()
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def admin_token(client):
    client.post("/api/v1/auth/register", json={
        "full_name": "Admin User", "email": "admin@test.com",
        "password": "AdminPass123", "role": "admin",
    })
    resp = client.post("/api/v1/auth/login-json", json={"email": "admin@test.com", "password": "AdminPass123"})
    return resp.json()["access_token"]


@pytest.fixture()
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
