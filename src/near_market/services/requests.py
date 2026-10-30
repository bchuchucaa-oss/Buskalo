
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement

from near_market.models import (
    RequestModel,
    CategoryModel,
    RequestBusinessMatchModel,
)
from near_market.schemas import RequestCreate
from near_market.services.businesses import find_matching_businesses



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

    db.delete(result)
    db.commit()


def create_request(
    db: Session,
    request: RequestCreate,
    user_id: uuid.UUID,
) -> RequestModel:

    category = db.scalar(
        select(CategoryModel).where(
            CategoryModel.id == request.category_id
        )
    )

    if category is None:
        raise HTTPException(
            status_code=422,
            detail="La categoría seleccionada no existe",
        )

    location = WKTElement(
        f"POINT({request.longitude} {request.latitude})",
        srid=4326,
    )

    new_request = RequestModel(
        user_id=user_id,
        descripcion=request.descripcion,
        category_id=category.id,
        ciudad=request.ciudad,
        latitud=request.latitude,
        longitud=request.longitude,
        location=location,
    )

    try:
        # 1. Agregar la solicitud sin confirmar la transacción.
        db.add(new_request)
        db.flush()

        # 2. Buscar negocios de la misma categoría dentro de 5 km.
        matching_businesses = find_matching_businesses(
            db=db,
            category_id=category.id,
            latitude=request.latitude,
            longitude=request.longitude,
            radius_meters=5000,
            limit=20,
        )

        # 3. Crear una coincidencia por cada negocio encontrado.
        for item in matching_businesses:
            match = RequestBusinessMatchModel(
                request_id=new_request.id,
                business_id=item["business"].id,
                distance_meters=item["distance_meters"],
                status="pending",
            )
            db.add(match)

        # 4. Confirmar solicitud y coincidencias juntas.
        db.commit()
        db.refresh(new_request)

    except Exception:
        db.rollback()
        raise

    return new_request