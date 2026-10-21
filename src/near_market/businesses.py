
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from near_market.models import BusinessModel
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
