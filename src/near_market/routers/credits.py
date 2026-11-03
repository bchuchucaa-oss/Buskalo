
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from near_market.database import get_db
from near_market.services.auth import get_current_user
from near_market.services.credits import (
    get_credit_balance,                                    
    create_credit_purchase,
    get_credit_transactions
)
from near_market.models import UserModel
from near_market.schemas import (
    CreditPurchaseCreate,
    CreditPurchaseResponse,
    CreditTransactionResponse
)

router = APIRouter(
    prefix="/credit-purchases",
    tags=["Credit purchases"],
)


@router.post(
    "",
    response_model=CreditPurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase(
    payload: CreditPurchaseCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    purchase = create_credit_purchase(
        db=db,
        user_id=current_user.id,
        package_type=payload.package_type,
    )

    return purchase

@router.get("/balance")
def get_balance(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    balance = get_credit_balance(
        db=db,
        user_id=current_user.id,
    )

    return {
        "user_id": current_user.id,
        "available_credits": balance,
    }
    
    
@router.get(
"/history",
response_model=list[CreditTransactionResponse],
)
def get_credit_history(
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
    ):
        return get_credit_transactions(
            db=db,
            user_id=current_user.id,
        )