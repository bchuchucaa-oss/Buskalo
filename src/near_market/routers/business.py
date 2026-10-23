
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from near_market.services.auth import get_current_user
from near_market.database import get_db
from near_market.models import UserModel
from near_market.schemas import BusinessCreate, BusinessResponse
from near_market.services.businesses import (
    create_business,
    get_all_businesses,
    get_business_by_id,
    update_business,
    delete_business,
    find_nearby_businesses,
)

router = APIRouter(prefix="/businesses", tags=["Businesses"])


@router.post(
    "",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_business_endpoint(
    business: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return create_business(db, business, current_user.id)


@router.get(
    "",
    response_model=list[BusinessResponse],
    status_code=status.HTTP_200_OK,
)
def get_businesses_endpoint(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return get_all_businesses(db, current_user.id)


@router.get("/nearby")
def get_nearby_businesses_endpoint(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: int = Query(default=5000, gt=0, le=100000),
    limit: int = Query(default=20, gt=0, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return find_nearby_businesses(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius_meters,
        limit=limit,
    )


@router.get("/{business_id}", response_model=BusinessResponse)
def get_business_endpoint(
    business_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return get_business_by_id(db, business_id, current_user.id)


@router.put("/{business_id}", response_model=BusinessResponse)
def update_business_endpoint(
    business_id: UUID,
    data: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return update_business(
        db,
        business_id,
        current_user.id,
        data,
    )


@router.delete(
    "/{business_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_business_endpoint(
    business_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    delete_business(db, business_id, current_user.id)
