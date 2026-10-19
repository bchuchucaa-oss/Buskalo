from fastapi.testclient import TestClient
from near_market.main import app
import uuid

client = TestClient(app)


def test_create_request_valid():
    response = client.post(
        "/requests",
        json={
            "descripcion": "Busco un cargador USB-C",
            "ciudad":"Cuenca",
             "categoria":"Electronicos"}
    )
    assert response.status_code == 201
    data = response.json()
    data.pop("id", None)
    data.pop("created_at",None)
    assert data == {
        "descripcion": "Busco un cargador USB-C",
                    "ciudad":"Cuenca",
                     "categoria":"Electronicos"
    }


def test_create_request_blank_description():
    response = client.post(
        "/requests",
        json={"descripcion": "   ",
              "ciudad":"Cuenca",
              "categoria":"Electronicos"}
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Descripcion invalida"


def test_create_request_description_too_long():
    response = client.post(
        "/requests",
        json={"descripcion": "a" * 201}
    )

    assert response.status_code == 422


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_request_and_list_it(client):
    payload = {
        "descripcion": "Busco un cargador USB-C",
        "categoria": "Electronica",
        "ciudad": "Giron",
    }

    # 1. Crear una solicitud
    create_response = client.post("/requests", json=payload)

    assert create_response.status_code == 201

    created_request = create_response.json()

    # 2. Verificar que la API devuelve un identificador
    assert "id" in created_request
    assert created_request["descripcion"] == payload["descripcion"]
    assert created_request["categoria"] == payload["categoria"]
    assert created_request["ciudad"] == payload["ciudad"]

    # 3. Consultar el listado
    list_response = client.get("/requests")

    assert list_response.status_code == 200

    requests = list_response.json()
    assert len(requests) == 1
    assert requests[0]["id"] == created_request["id"]


def test_get_and_delete_request(client):
    payload = {
        "descripcion": "Necesito un electricista",
        "categoria": "Servicios",
        "ciudad": "Giron",
    }

    # Crear una solicitud para esta prueba
    create_response = client.post("/requests", json=payload)
    assert create_response.status_code == 201

    request_id = create_response.json()["id"]

    # Consultar por UUID
    get_response = client.get(f"/requests/{request_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == request_id

    # Eliminar la solicitud
    delete_response = client.delete(f"/requests/{request_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # Confirmar que ya no existe
    missing_response = client.get(f"/requests/{request_id}")
    assert missing_response.status_code == 404

