
import uuid
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy import select
from near_market.models.request_business_match import RequestBusinessMatchModel
from near_market.websocket_manager import manager
from sqlalchemy.orm import Session
from near_market.services.auth import get_current_user
from near_market.database import get_db
from near_market.models import UserModel
from near_market.schemas import RequestCreate, RequestResponse
from near_market.services.requests import (
    create_request,
    get_all_requests,
    requests_by_id,
    delete_by_id,
)
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post(
    "",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_request_endpoint(
    request: RequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> RequestResponse:

    new_request = create_request(db, request, current_user.id)

    business_ids = [
        match.business_id
        for match in db.scalars(
            select(RequestBusinessMatchModel).where(
                RequestBusinessMatchModel.request_id == new_request.id
            )
        ).all()
    ]

    background_tasks.add_task(
        notify_matching_businesses,
        business_ids,
        new_request.id,
    )

    return new_request


@router.get(
    "",
    response_model=list[RequestResponse],
    status_code=status.HTTP_200_OK,
)
def get_requests_endpoint(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return get_all_requests(db, current_user.id)


@router.get("/{request_id}", response_model=RequestResponse)
def get_request_endpoint(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return requests_by_id(db, request_id, current_user.id)


@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_request_endpoint(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    delete_by_id( request_id = request_id, db = db, user_id = current_user.id)


async def notify_matching_businesses(
    business_ids: list[uuid.UUID],
    request_id: uuid.UUID,
):
    for business_id in business_ids:
        try:
            await manager.send_to_business(
                business_id,
                {
                    "type": "new_request",
                    "request_id": str(request_id),
                    "message": "Tienes una nueva solicitud",
            },
            )
        except Exception:
            logger.exception(
                "Error notificando al negocio %s",
                business_id,
            )