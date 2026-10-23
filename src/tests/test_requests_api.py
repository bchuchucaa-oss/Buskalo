from fastapi.testclient import TestClient
from near_market.main import app
import uuid
import pytest


client = TestClient(app)


def test_create_request_valid(client, auth_headers):

    response = client.post(
        "/requests",
        headers = auth_headers,
        json={
            "descripcion": "Busco un cargador USB-C",
            "ciudad":"Cuenca",
             "categoria":"Electronicos", 
            "latitude": -2.9001,
             "longitude": -79.0059,}
    )
    assert response.status_code == 201
    data = response.json()
    data.pop("id", None)
    data.pop("created_at",None)
    data.pop("latitude", None)
    data.pop("longitude", None)
    assert data == {
        "descripcion": "Busco un cargador USB-C",
                    "ciudad":"Cuenca",
                     "categoria":"Electronicos",
    }


def test_create_request_blank_description(auth_headers):
    response = client.post(
        "/requests",
        headers= auth_headers,
        json={"descripcion": "   ",
              "ciudad":"Cuenca",
              "categoria":"Electronicos"}
    )

    assert response.status_code == 422
    errors = response.json()["detail"]

    assert any(
        error["loc"][-1] == "descripcion"
        and "no puede estar vacio" in error["msg"]
        for error in errors
    )


def test_create_request_description_too_long(auth_headers):
    response = client.post(
        "/requests",
        headers = auth_headers,
        json={"descripcion": "a" * 201}
    )

    assert response.status_code == 422


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_request_and_list_it(client, auth_headers):
    payload = {
        "descripcion": "Busco un cargador USB-C",
        "categoria": "Electronica",
        "ciudad": "Giron",
        "latitude": -2.9001,
        "longitude": -79.0059
    }

    # 1. Crear una solicitud
    create_response = client.post("/requests", headers= auth_headers,json=payload)

    assert create_response.status_code == 201

    created_request = create_response.json()

    # 2. Verificar que la API devuelve un identificador
    assert "id" in created_request
    assert created_request["descripcion"] == payload["descripcion"]
    assert created_request["categoria"] == payload["categoria"]
    assert created_request["ciudad"] == payload["ciudad"]

    # 3. Consultar el listado
    list_response = client.get("/requests", headers= auth_headers)

    assert list_response.status_code == 200

    requests = list_response.json()
    assert len(requests) == 1
    assert requests[0]["id"] == created_request["id"]


def test_get_and_delete_request(client, auth_headers):
    payload = {
        "descripcion": "Necesito un electricista",
        "categoria": "Servicios",
        "ciudad": "Giron",
         "latitude": -2.9001,
        "longitude": -79.0059,
    }

    # Crear una solicitud para esta prueba
    create_response = client.post("/requests", headers=auth_headers, json=payload)
    assert create_response.status_code == 201

    request_id = create_response.json()["id"]

    # Consultar por UUID
    get_response = client.get(f"/requests/{request_id}", headers= auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == request_id

    # Eliminar la solicitud
    delete_response = client.delete(f"/requests/{request_id}", headers = auth_headers)
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # Confirmar que ya no existe
    missing_response = client.get(f"/requests/{request_id}", headers = auth_headers)
    assert missing_response.status_code == 404





def test_create_request_without_token_returns_401(client):
    response = client.post(
        "/requests",
        json={
            "descripcion": "Busco un cargador USB-C",
            "ciudad": "Cuenca",
            "categoria": "Electronicos",
        },
    )

    assert response.status_code == 401


def test_user_cannot_access_another_users_request(
    client,
    auth_headers,
    other_auth_headers,
):
    create_response = client.post(
        "/requests",
        headers=auth_headers,
        json={
            "descripcion": "Busco un cargador USB-C",
            "ciudad": "Cuenca",
            "categoria": "Electronicos",
             "latitude": -2.9001,
            "longitude": -79.0059,
        },
    )

    assert create_response.status_code == 201, create_response.text
    request_id = create_response.json()["id"]

    # El segundo usuario no debe poder consultar la solicitud.
    get_response = client.get(
        f"/requests/{request_id}",
        headers=other_auth_headers,
    )

    assert get_response.status_code == 404, get_response.text

    # Tampoco debe poder eliminarla.
    delete_response = client.delete(
        f"/requests/{request_id}",
        headers=other_auth_headers,
    )

    assert delete_response.status_code == 404, delete_response.text

    # El propietario todavía debe poder consultarla.
    owner_response = client.get(
        f"/requests/{request_id}",
        headers=auth_headers,
    )

    assert owner_response.status_code == 200, owner_response.text

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("descripcion", ""),
        ("descripcion", "   "),
        ("categoria", ""),
        ("categoria", "   "),
        ("ciudad", ""),
        ("ciudad", "   "),
    ],
)
def test_create_request_rejects_empty_text(
    client,
    auth_headers,
    field,
    value,
):
    payload = {
        "descripcion": "Busco un cargador USB-C",
        "categoria": "Electronicos",
        "ciudad": "Cuenca",
    }
    payload[field] = value

    response = client.post(
        "/requests",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == 422, response.text
