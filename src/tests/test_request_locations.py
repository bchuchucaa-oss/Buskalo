from sqlalchemy import func, select

from near_market.models import RequestModel


def test_request_location_matches_coordinates_and_uses_wgs84(
    client,
    auth_headers,
    db_session,
    test_category
):
    latitude = -3.16
    longitude = -79.14
    response = client.post(
        "/requests",
        headers=auth_headers,
        json={
            "descripcion": "Necesito un electricista",
            "category_id": str(test_category.id),            "ciudad": "Girón",
            "latitude": latitude,
            "longitude": longitude,
        },
    )

    assert response.status_code == 201, response.text
    request_id = response.json()["id"]
    stored_latitude, stored_longitude, srid = db_session.execute(
        select(
            func.ST_Y(RequestModel.location),
            func.ST_X(RequestModel.location),
            func.ST_SRID(RequestModel.location),
        ).where(RequestModel.id == request_id)
    ).one()

    assert stored_latitude == latitude
    assert stored_longitude == longitude
    assert srid == 4326
