
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from near_market.models.models import RequestModel
from near_market.schemas import RequestCreate

from geoalchemy2 import WKTElement

def create_request(db: Session, request: RequestCreate, user_id: uuid.UUID) -> RequestModel:

    location = WKTElement(
            f"POINT({request.longitude} {request.latitude})",
            srid=4326,
        )
    
    new_request = RequestModel(
        id=uuid.uuid4(),
        user_id= user_id,
        descripcion=request.descripcion,
        categoria=request.categoria,
        ciudad=request.ciudad,
        latitud = request.latitude,
        longitud = request.longitude,
        location= location
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


def get_all_requests(db: Session, user_id) -> list[RequestModel]:
    statement =( select(RequestModel)
    .where(RequestModel.user_id == user_id)
    .order_by(
        RequestModel.created_at.desc()
    ))
    return list(db.scalars(statement).all())


def requests_by_id(
    db: Session,
    request_id: uuid.UUID,
    user_id) -> RequestModel:

    statement = select(RequestModel).where(
        RequestModel.id == request_id,
        RequestModel.user_id == user_id
    )

    result = db.scalar(statement)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Request not found",
        )

    return result


def delete_by_id(
        request_id: uuid.UUID,
    db: Session,
    user_id
    
) -> None:
    
    result = requests_by_id(db, request_id, user_id)
    
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Request not found",
        )

    db.delete(result)
    db.commit()
