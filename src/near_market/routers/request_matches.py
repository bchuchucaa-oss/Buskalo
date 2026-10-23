
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

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
            RequestBusinessMatchModel.business_id,
            BusinessModel.name.label("business_name"),
            RequestBusinessMatchModel.distance_meters,
            RequestBusinessMatchModel.status,
        )
        .join(
            BusinessModel,
            BusinessModel.id == RequestBusinessMatchModel.business_id,
        )
        .where(RequestBusinessMatchModel.request_id == request_id)
        .order_by(RequestBusinessMatchModel.distance_meters)
    ).all()

    return [
        RequestMatchResponse(
            business_id=row.business_id,
            business_name=row.business_name,
            distance_meters=row.distance_meters,
            status=row.status,
        )
        for row in results
    ]


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

    match.status = payload.status
    match.price = payload.price
    match.notes = payload.notes
    match.responded_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(match)

    return {
        "id": str(match.id),
        "status": match.status,
        "price": payload.price,
        "notes": payload.notes,
    }
