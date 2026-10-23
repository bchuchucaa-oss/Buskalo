
import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from near_market.main import app
from near_market.database import get_db
from near_market.database import Base
from near_market.models import models  # Registra los modelos en Base.metadata

load_dotenv()

@pytest.fixture
def reset_database():
    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        pytest.fail(
            "Falta TEST_DATABASE_URL. Revisa la configuracion del archivo .env."
        )

    if not database_url.endswith("/nearmarket_test"):
        pytest.fail(
            "Por seguridad, TEST_DATABASE_URL debe apuntar a nearmarket_test."
        )

    engine = create_engine(database_url)

    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def db_session(reset_database):
    TestingSessionLocal = sessionmaker(
        bind=reset_database,
        autoflush=False,
        expire_on_commit=False,
    )

    with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@test.com",
            "password": "test_user",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@test.com",
            "password": "test_user",
        },
    )

    assert response.status_code == 200, response.text

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "other@test.com",
            "password": "other_user_123",
            "full_name": "Other User",
        },
    )
    assert response.status_code == 201, response.text

    response = client.post(
        "/auth/login",
        json={
            "email": "other@test.com",
            "password": "other_user_123",
        },
    )
    assert response.status_code == 200, response.text

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
