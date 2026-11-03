
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from near_market.services.auth import get_current_admin
from near_market.database import get_db
from near_market.models import UserModel
from near_market.services.credits import (
    approve_credit_purchase,
    get_pending_credit_purchases)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.patch(
    "/credit-purchases/{purchase_id}/approve",
    status_code=status.HTTP_200_OK,
)
def approve_purchase(
    purchase_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin),
):
    purchase = approve_credit_purchase(
        db=db,
        purchase_id=purchase_id,
        admin_id=current_admin.id,
    )

    return {
        "id": str(purchase.id),
        "user_id": str(purchase.user_id),
        "amount": purchase.amount,
        "credits": purchase.credits,
        "status": purchase.status,
        "approved_at": purchase.approved_at,
    }

@router.get("/credit-purchases/pending")
def list_pending_purchases(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin),
):
    purchases = get_pending_credit_purchases(db)

    return [
        {
            "id": str(purchase.id),
            "user_id": str(purchase.user_id),
            "full_name": full_name,
            "email": email,
            "package_type": purchase.package_type,
            "amount": purchase.amount,
            "credits": purchase.credits,
            "status": purchase.status,
            "payment_reference": purchase.payment_reference,
            "created_at": purchase.created_at,
        }
        for purchase, full_name, email in purchases
    ]