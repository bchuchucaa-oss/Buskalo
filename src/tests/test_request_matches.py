import uuid

from sqlalchemy import func

from near_market.models.credit import CreditTransactionModel


def test_business_cannot_respond_to_another_business_match(
    client,
    other_auth_headers,
    test_match,
    db_session,
):
    response = client.patch(
        f"/request-matches/{test_match.id}",
        headers=other_auth_headers,
        json={
            "status": "available",
            "price": 25.00,
            "notes": "Servicio disponible",
        },
    )

    assert response.status_code == 404

    db_session.refresh(test_match)

    assert test_match.status == "pending"
    assert test_match.price is None
    assert test_match.responded_at is None
    
def test_business_owner_can_respond_to_own_match(
    client,
    auth_headers,
    test_match,
):
    response = client.patch(
        f"/request-matches/{test_match.id}",
        headers=auth_headers,
        json={
            "status": "available",
            "price": 25.00,
            "notes": "Servicio disponible",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "available"
    assert float(response.json()["price"]) == 25.00
    assert response.json()["notes"] == "Servicio disponible"
    
def test_business_cannot_respond_to_match_twice(
    client,
    auth_headers,
    test_match,
):
    payload = {
        "status": "available",
        "price": 25.00,
        "notes": "Servicio disponible",
    }

    first_response = client.patch(
        f"/request-matches/{test_match.id}",
        headers=auth_headers,
        json=payload,
    )

    assert first_response.status_code == 200

    second_response = client.patch(
        f"/request-matches/{test_match.id}",
        headers=auth_headers,
        json={
            "status": "unavailable",
            "notes": "Ya no está disponible",
        },
    )

    assert second_response.status_code == 409
    
def test_user_cannot_access_another_users_matches(
    client,
    other_auth_headers,
    test_request,
):
    response = client.get(
        f"/requests/{test_request.id}/matches",
        headers=other_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Solicitud no encontrada"
    
def test_user_cannot_unlock_another_users_match(
    client,
    other_auth_headers,
    test_match,
    db_session,
):
    response = client.post(
        f"/request-matches/{test_match.id}/unlock",
        headers=other_auth_headers,
    )

    assert response.status_code == 404

    db_session.refresh(test_match)
    assert test_match.unlocked_at is None
    
def test_unlock_contact_consumes_only_one_credit(
    client,
    auth_headers,
    test_user,
    test_match,
    db_session,
):
    # Preparar una oferta disponible
    test_match.status = "available"
    test_match.price = 25.00

    # Darle un crédito al cliente
    transaction = CreditTransactionModel(
        user_id=uuid.UUID(test_user["id"]),
        credits=1,
        transaction_type="purchase",
        description="Crédito para pruebas",
    )

    db_session.add(transaction)
    db_session.commit()

    # Primer desbloqueo
    response = client.post(
        f"/request-matches/{test_match.id}/unlock",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text

    db_session.refresh(test_match)
    assert test_match.unlocked_at is not None

    # Segundo desbloqueo: debe ser idempotente
    response = client.post(
        f"/request-matches/{test_match.id}/unlock",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text

    # Solo debe existir un débito
    balance = (
        db_session.query(
            func.coalesce(func.sum(CreditTransactionModel.credits), 0)
        )
        .filter(CreditTransactionModel.user_id == uuid.UUID(test_user["id"]))
        .scalar()
    )

    assert balance == 0
    
def test_user_cannot_unlock_without_credits(
    client,
    auth_headers,
    test_match,
    db_session,
):
    test_match.status = "available"
    test_match.price = 25.00
    db_session.commit()

    response = client.post(
        f"/request-matches/{test_match.id}/unlock",
        headers=auth_headers,
    )

    db_session.refresh(test_match)
    assert test_match.unlocked_at is None

    db_session.refresh(test_match)
    assert test_match.unlocked_at is None