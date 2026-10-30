
from uuid import UUID

from fastapi import APIRouter, Depends, status
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

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post(
    "",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_request_endpoint(
    request: RequestCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
)-> RequestResponse:
    return create_request(db, request, current_user.id)


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
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    return requests_by_id(db, request_id, current_user.id)


@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_request_endpoint(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    delete_by_id( request_id = request_id, db = db, user_id = current_user.id)
