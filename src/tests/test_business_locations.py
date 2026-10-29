import pytest
from sqlalchemy import func, select

from near_market.models import BusinessModel


def _business_payload(name, latitude, longitude):
    return {
        "name": name,
        "description": None,
        "address": None,
        "city": "Girón",
        "latitude": latitude,
        "longitude": longitude,
    }


def _point_coordinates(db_session, business_id):
    return db_session.execute(
        select(
            func.ST_Y(BusinessModel.location),
            func.ST_X(BusinessModel.location),
        ).where(BusinessModel.id == business_id)
    ).one()


def test_business_location_stays_in_sync_on_create_and_update(
    client,
    auth_headers,
    db_session,
):
    created = client.post(
        "/businesses",
        headers=auth_headers,
        json=_business_payload("Tienda", -3.16, -79.14),
    )

    assert created.status_code == 201, created.text
    business = created.json()
    assert _point_coordinates(db_session, business["id"]) == (-3.16, -79.14)

    updated = client.put(
        f"/businesses/{business['id']}",
        headers=auth_headers,
        json=_business_payload("Tienda actualizada", -3.17, -79.15),
    )

    assert updated.status_code == 200, updated.text
    assert updated.json()["latitude"] == -3.17
    assert updated.json()["longitude"] == -79.15
    assert _point_coordinates(db_session, business["id"]) == (-3.17, -79.15)


def test_nearby_businesses_apply_radius_and_distance_order(
    client,
    auth_headers,
):
    origin_latitude = -3.16
    origin_longitude = -79.14
    businesses = [
        ("Lejano", origin_latitude, origin_longitude + 0.01),
        ("Cercano", origin_latitude, origin_longitude + 0.001),
        ("En origen", origin_latitude, origin_longitude),
    ]

    for name, latitude, longitude in businesses:
        response = client.post(
            "/businesses",
            headers=auth_headers,
            json=_business_payload(name, latitude, longitude),
        )
        assert response.status_code == 201, response.text

    response = client.get(
        "/businesses/nearby",
        headers=auth_headers,
        params={
            "latitude": origin_latitude,
            "longitude": origin_longitude,
            "radius_meters": 500,
        },
    )

    assert response.status_code == 200, response.text
    results = response.json()
    assert [item["business"]["name"] for item in results] == [
        "En origen",
        "Cercano",
    ]
    assert [item["distance_meters"] for item in results] == sorted(
        item["distance_meters"] for item in results
    )
    assert all(item["distance_meters"] <= 500 for item in results)


def test_nearby_businesses_requires_authentication(client):
    response = client.get(
        "/businesses/nearby",
        params={"latitude": -3.16, "longitude": -79.14},
    )

    assert response.status_code == 401


def test_nearby_businesses_reject_invalid_radius(client, auth_headers):
    response = client.get(
        "/businesses/nearby",
        headers=auth_headers,
        params={
            "latitude": -3.16,
            "longitude": -79.14,
            "radius_meters": 0,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [(-3.16, None), (None, -79.14)],
)
def test_business_rejects_partial_coordinates(
    client,
    auth_headers,
    latitude,
    longitude,
):
    payload = _business_payload("Tienda", -3.16, -79.14)
    payload["latitude"] = latitude
    payload["longitude"] = longitude

    response = client.post(
        "/businesses",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == 422, response.text

@pytest.mark.parametrize(
    "missing_coordinate",
    ["latitude", "longitude", "both"],
)
def test_business_requires_coordinates(
    client,
    auth_headers,
    missing_coordinate,
):
    payload = _business_payload("Tienda", -3.16, -79.14)

    if missing_coordinate in ("latitude", "both"):
        payload.pop("latitude")

    if missing_coordinate in ("longitude", "both"):
        payload.pop("longitude")

    response = client.post(
        "/businesses",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == 422, response.text
    
@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [
        (-91, -79.14),
        (91, -79.14),
        (-3.16, -181),
        (-3.16, 181),
    ],
)
def test_business_rejects_out_of_range_coordinates(
    client,
    auth_headers,
    latitude,
    longitude,
):
    response = client.post(
        "/businesses",
        headers=auth_headers,
        json=_business_payload("Tienda", latitude, longitude),
    )

    assert response.status_code == 422, response.text