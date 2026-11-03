
import uuid


def test_regular_user_cannot_list_pending_credit_purchases(
    client,
    auth_headers,
):
    response = client.get(
        "/admin/credit-purchases/pending",
        headers=auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "No tienes permisos de administrador"
    )


def test_regular_user_cannot_approve_credit_purchase(
    client,
    auth_headers,
):
    purchase_id = uuid.uuid4()

    response = client.patch(
        f"/admin/credit-purchases/{purchase_id}/approve",
        headers=auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "No tienes permisos de administrador"
    )
