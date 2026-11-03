
from datetime import datetime, timezone
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from near_market.services.credits import unlock_business_contact
from near_market.services.auth import get_current_user
from near_market.database import get_db
from near_market.models import (
    BusinessModel,
    RequestModel,
    RequestBusinessMatchModel,
    UserModel,
)
from near_market.schemas import MatchResponseCreate, RequestMatchResponse

router = APIRouter(tags=["Request Matches"])


@router.get(
    "/requests/{request_id}/matches",
    response_model=list[RequestMatchResponse],
)
def get_request_matches(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    request_record = db.scalar(
        select(RequestModel).where(
            RequestModel.id == request_id,
            RequestModel.user_id == current_user.id,
        )
    )

    if request_record is None:
        raise HTTPException(
            status_code=404,
            detail="Solicitud no encontrada",
        )

    results = db.execute(
    select(
        RequestBusinessMatchModel,
        BusinessModel,
    )
    .join(
        RequestModel,
        RequestModel.id == RequestBusinessMatchModel.request_id,
    )
    .join(
        BusinessModel,
        BusinessModel.id == RequestBusinessMatchModel.business_id,
    )
    .where(
        RequestBusinessMatchModel.request_id == request_id,
        RequestModel.user_id == current_user.id,
    )
    .order_by(RequestBusinessMatchModel.distance_meters)
    ).all()

    response = []

    for match, business in results:
        unlocked = match.unlocked_at is not None

        if match.distance_meters < 1000:
            distance_range = "<1 km"
        elif match.distance_meters < 3000:
            distance_range = "1-3 km"
        elif match.distance_meters < 5000:
            distance_range = "3-5 km"
        else:
            distance_range = "5+ km"

        response.append(
            RequestMatchResponse(
                match_id=match.id,
                status=match.status,
                price=match.price,
                city=business.city,
                distance_range=distance_range,
                unlocked=unlocked,
                business_name=business.name if unlocked else None,
                address=business.address if unlocked else None,
                phone=business.phone if unlocked else None,
                whatsapp=business.whatsapp if unlocked else None,
            )
        )

    return response


@router.patch("/request-matches/{match_id}")
def update_match_response(
    match_id: UUID,
    payload: MatchResponseCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    match = db.scalar(
    select(RequestBusinessMatchModel)
    .join(
        BusinessModel,
        BusinessModel.id == RequestBusinessMatchModel.business_id,
    )
    .where(
        RequestBusinessMatchModel.id == match_id,
        BusinessModel.owner_id == current_user.id,
    )
    .with_for_update()
    )

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Coincidencia no encontrada",
        )

    if match.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Esta coincidencia ya fue respondida",
        )

    if payload.status == "available" and payload.price is None:
        raise HTTPException(
            status_code=422,
            detail="Debes indicar el precio cuando el producto o servicio está disponible",
        )

    try:
        match.status = payload.status
        match.price = payload.price
        match.notes = payload.notes
        match.responded_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(match)

    except Exception:
        db.rollback()
        raise

    return {
        "id": str(match.id),
        "status": match.status,
        "price": match.price,
        "notes": match.notes,
    }
    
@router.post("/request-matches/{match_id}/unlock")
def unlock_match(
    match_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return unlock_business_contact(
        db=db,
        match_id=match_id,
        user_id=current_user.id,
    )