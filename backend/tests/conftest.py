"""Test setup: every test gets a fresh in-memory SQLite database.

The production PostgreSQL database is never touched: get_db is overridden
so the API talks to a throwaway engine created here.
"""
import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def plan(client):
    response = client.post("/api/plans", json={"name": "Monthly", "duration_months": 1, "price": 1500})
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def trainer(client):
    response = client.post(
        "/api/trainers", json={"name": "Rohit Sharma", "specialization": "Strength", "experience_years": 5}
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def member(client, plan, trainer):
    response = client.post(
        "/api/members",
        json={
            "full_name": "Himanshu Chauhan",
            "email": "himanshu@example.com",
            "phone": "9999999999",
            "gender": "MALE",
            "plan_id": plan["id"],
            "trainer_id": trainer["id"],
        },
    )
    assert response.status_code == 201
    return response.json()
