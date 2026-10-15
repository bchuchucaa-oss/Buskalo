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