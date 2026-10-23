
import uuid

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from geoalchemy2 import Geography

from near_market.models.models import BusinessModel
from near_market.schemas import BusinessCreate


def create_business(
    db: Session,
    business: BusinessCreate,
    owner_id: uuid.UUID,
) -> BusinessModel:
    new_business = BusinessModel(
        owner_id=owner_id,
        name=business.name,
        description=business.description,
        address=business.address,
        city=business.city,
        latitude=business.latitude,
        longitude=business.longitude,
        location = build_location(
            business.latitude,
            business.longitude
        )
    )

    db.add(new_business)
    db.commit()
    db.refresh(new_business)

    return new_business


def get_all_businesses(
    db: Session,
    owner_id: uuid.UUID,
) -> list[BusinessModel]:
    statement = (
        select(BusinessModel)
        .where(BusinessModel.owner_id == owner_id)
        .order_by(BusinessModel.created_at.desc())
    )

    return list(db.scalars(statement).all())


def get_business_by_id(
    db: Session,
    business_id: uuid.UUID,
    owner_id: uuid.UUID,
) -> BusinessModel:
    statement = select(BusinessModel).where(
        BusinessModel.id == business_id,
        BusinessModel.owner_id == owner_id,
    )

    business = db.scalar(statement)

    if business is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    return business


def update_business(
    db: Session,
    business_id: uuid.UUID,
    owner_id: uuid.UUID,
    data: BusinessCreate,
) -> BusinessModel:
    business = get_business_by_id(db, business_id, owner_id)

    business.name = data.name
    business.description = data.description
    business.address = data.address
    business.city = data.city
    business.latitude = data.latitude
    business.longitude = data.longitude
    business.location = build_location(
        data.latitude,
        business.longitude
    )
    db.commit()
    db.refresh(business)

    return business


def delete_business(
    db: Session,
    business_id: uuid.UUID,
    owner_id: uuid.UUID,
) -> None:
    business = get_business_by_id(db, business_id, owner_id)

    db.delete(business)
    db.commit()

def build_location(
    latitude: float | None,
    longitude: float | None,
):
    if latitude is None or longitude is None:
        return None

    return WKTElement(
        f"POINT({longitude} {latitude})",
        srid=4326,
    )

def find_nearby_businesses(
    db: Session,
    latitude: float,
    longitude: float,
    radius_meters: int = 5000,
    limit: int = 20,
):
    """Find businesses within a radius, ordered by distance."""

    origin = func.ST_SetSRID(
        func.ST_MakePoint(longitude, latitude),
        4326,
    ).cast(Geography(srid=4326))

    business_location = BusinessModel.location.cast(
        Geography(srid=4326)
    )

    distance = func.ST_Distance(
        business_location,
        origin,
    ).label("distance_meters")

    statement = (
        select(BusinessModel, distance)
        .where(BusinessModel.location.is_not(None))
        .where(
            func.ST_DWithin(
                business_location,
                origin,
                radius_meters,
            )
        )
        .order_by(distance)
        .limit(limit)
    )

    results = db.execute(statement).all()

    return [
        {
            "business": business,
            "distance_meters": round(float(distance_meters), 2),
        }
        for business, distance_meters in results
    ]
