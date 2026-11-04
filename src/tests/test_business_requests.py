from near_market.models.request import RequestModel
from near_market.models.request_business_match import RequestBusinessMatchModel

def test_get_business_requests_returns_owner_matches(
    client,
    auth_headers,
    test_match,
):
    response = client.get(
        "/businesses/me/requests",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    match = data[0]

    assert match["match_id"] == str(test_match.id)
    assert match["request_id"] == str(test_match.request_id)
    assert match["business_id"] == str(test_match.business_id)
    assert match["status"] == "pending"
    assert match["descripcion"] == "Necesito un servicio de plomería"
    assert match["category_name"] == "Plomería"



def test_get_business_requests_does_not_return_other_owner_matches(
    client,
    auth_headers,
    other_business,
    test_match,
):
    response = client.get(
        "/businesses/me/requests",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["business_id"] == str(test_match.business_id)

    assert data[0]["business_id"] != other_business["id"]




def test_get_business_requests_filters_by_status(
    client,
    auth_headers,
    test_match,
    db_session,
):
    second_request = RequestModel(
        user_id=test_match.request.user_id,
        descripcion="Necesito reparar una tubería",
        category_id=test_match.request.category_id,
        ciudad="Girón",
        latitud=-3.16,
        longitud=-79.14,
    )

    db_session.add(second_request)
    db_session.flush()

    available_match = RequestBusinessMatchModel(
        request_id=second_request.id,
        business_id=test_match.business_id,
        distance_meters=150.0,
        status="available",
    )

    db_session.add(available_match)
    db_session.commit()

    response = client.get(
        "/businesses/me/requests?status=pending",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["status"] == "pending"
    assert data[0]["match_id"] == str(test_match.id)




def test_get_business_requests_returns_empty_list_without_businesses(
    client,
    other_auth_headers,
):
    response = client.get(
        "/businesses/me/requests",
        headers=other_auth_headers,
    )

    assert response.status_code == 200

    assert response.json() == []
