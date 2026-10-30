from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from near_market.models import (
    RequestBusinessMatchModel,
    BusinessModel,
    RequestModel,
    BusinessCategoryModel,
)


def get_business_matches(
    db: Session,
    owner_id: UUID,
    limit: int = 20,
    offset: int = 0,
):
    filters = (
        BusinessModel.owner_id == owner_id,
    )

    total_statement = (
        select(func.count(RequestBusinessMatchModel.id))
        .join(
            BusinessModel,
            BusinessModel.id == RequestBusinessMatchModel.business_id,
        )
        .where(*filters)
    )

    total = db.scalar(total_statement) or 0

    statement = (
        select(RequestBusinessMatchModel)
        .join(
            BusinessModel,
            BusinessModel.id == RequestBusinessMatchModel.business_id,
        )
        .where(*filters)
        .options(
            selectinload(RequestBusinessMatchModel.business)
            .selectinload(BusinessModel.business_categories)
            .selectinload(BusinessCategoryModel.category)
        )
        .options(
            selectinload(RequestBusinessMatchModel.request)
            .selectinload(RequestModel.category)
        )
        .order_by(
            RequestBusinessMatchModel.created_at.desc(),
            RequestBusinessMatchModel.distance_meters.asc(),
        )
        .limit(limit)
        .offset(offset)
    )

    matches = list(db.scalars(statement).all())

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "matches": matches,
    }