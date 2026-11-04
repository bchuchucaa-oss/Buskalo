
import os
import uuid

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from near_market.main import app
from near_market.database import get_db
from near_market.database import Base
from near_market.models import models
from near_market.models.category import CategoryModel
from near_market.models.request import RequestModel
from near_market.models.request_business_match import RequestBusinessMatchModel 
 # Registra los modelos en Base.metadata

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
def other_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "other@test.com",
            "password": "other_user_123",
            "full_name": "Other User",
        },
    )

    assert response.status_code == 201, response.text
    return response.json()

# @pytest.fixture
# def other_auth_headers(client, other_user):
#     response = client.post(
#         "/auth/login",
#         json={
#             "email": "other@test.com",
#             "password": "other_user_123",
#         },
#     )

#     assert response.status_code == 200, response.text

#     token = response.json()["access_token"]
#     return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_category(db_session):
    category = CategoryModel(name="Plomería")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    return category

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

@pytest.fixture
def test_business(client, auth_headers, test_category):
    payload = {
        "name": "Negocio principal",
        "description": None,
        "address": None,
        "city": "Girón",
        "latitude": -3.16,
        "longitude": -79.14,
        "category_ids": [str(test_category.id)],
    }

    response = client.post(
        "/businesses",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == 201, response.text
    return response.json()

@pytest.fixture
def other_business(client, other_auth_headers, test_category):
    payload = {
        "name": "Negocio secundario",
        "description": None,
        "address": None,
        "city": "Girón",
        "latitude": -3.17,
        "longitude": -79.15,
        "category_ids": [str(test_category.id)],
    }

    response = client.post(
        "/businesses",
        headers=other_auth_headers,
        json=payload,
    )

    assert response.status_code == 201, response.text
    return response.json()

@pytest.fixture
def test_request(db_session, test_user, test_category):
    request = RequestModel(
        user_id=uuid.UUID(test_user["id"]),
        descripcion="Necesito un servicio de plomería",
        category_id=test_category.id,
        ciudad="Girón",
        latitud=-3.16,
        longitud=-79.14,
    )

    db_session.add(request)
    db_session.commit()
    db_session.refresh(request)

    return request

@pytest.fixture
def test_match(db_session, test_request, test_business):
    match = RequestBusinessMatchModel(
        request_id=test_request.id,
        business_id=uuid.UUID(test_business["id"]),
        distance_meters=150.0,
        status="pending",
    )

    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)

    return match