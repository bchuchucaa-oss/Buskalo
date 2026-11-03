
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from decimal import Decimal

from near_market.models import (
    CreditPurchaseModel,
    CreditTransactionModel,
    RequestModel,
    RequestBusinessMatchModel,
    UserModel
)

def approve_credit_purchase(
    db: Session,
    purchase_id: uuid.UUID,
    admin_id: uuid.UUID,
) -> CreditPurchaseModel:

    purchase = db.scalar(
        select(CreditPurchaseModel)
        .where(CreditPurchaseModel.id == purchase_id)
        .with_for_update()
    )

    if purchase is None:
        raise HTTPException(
            status_code=404,
            detail="Compra no encontrada",
        )

    if purchase.status != "pending_review":
        raise HTTPException(
            status_code=409,
            detail="Esta compra ya fue revisada",
        )

    try:
        purchase.status = "approved"
        purchase.approved_at = datetime.now(timezone.utc)
        purchase.reviewed_by = admin_id

        transaction = CreditTransactionModel(
            user_id=purchase.user_id,
            purchase_id=purchase.id,
            credits=purchase.credits,
            transaction_type="purchase",
            description=(
                f"Compra de {purchase.credits} créditos "
                f"por ${purchase.amount}"
            ),
        )

        db.add(transaction)
        db.commit()
        db.refresh(purchase)

        return purchase

    except Exception:
        db.rollback()
        raise
CREDIT_PACKAGES = {
    "single": {
        "amount": Decimal("1.00"),
        "credits": 1,
    },
    "pack_5": {
        "amount": Decimal("2.50"),
        "credits": 5,
    },
}


def create_credit_purchase(
    db: Session,
    user_id: uuid.UUID,
    package_type: str,
) -> CreditPurchaseModel:

    package = CREDIT_PACKAGES.get(package_type)

    if package is None:
        raise ValueError("Paquete de créditos no válido")

    purchase = CreditPurchaseModel(
        user_id=user_id,
        package_type=package_type,
        amount=package["amount"],
        credits=package["credits"],
        status="pending_review",
        payment_reference=f"NM-{uuid.uuid4().hex[:12].upper()}",
    )

    try:
        db.add(purchase)
        db.commit()
        db.refresh(purchase)

    except Exception:
        db.rollback()
        raise

    return purchase

def get_credit_balance(
    db: Session,
    user_id: uuid.UUID,
) -> int:
    balance = db.scalar(
        select(
            func.coalesce(
                func.sum(CreditTransactionModel.credits),
                0,
            )
        ).where(
            CreditTransactionModel.user_id == user_id
        )
    )

    return int(balance)

def unlock_business_contact(
    db: Session,
    match_id: uuid.UUID,
    user_id: uuid.UUID,
):
    try:
        # 1. Bloquear la fila del usuario para evitar
        # consumos simultáneos de sus créditos.
        user = db.scalar(
            select(UserModel)
            .where(UserModel.id == user_id)
            .with_for_update()
        )

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado",
            )

        # 2. Buscar y bloquear la coincidencia.
        match = db.scalar(
            select(RequestBusinessMatchModel)
            .join(
                RequestModel,
                RequestModel.id == RequestBusinessMatchModel.request_id,
            )
            .where(
                RequestBusinessMatchModel.id == match_id,
                RequestModel.user_id == user_id,
            )
            .with_for_update(of=RequestBusinessMatchModel)
        )

        if match is None:
            raise HTTPException(
                status_code=404,
                detail="Coincidencia no encontrada",
            )

        # 3. Evitar cobrar dos veces.
        if match.unlocked_at is not None:
            db.commit()
            return {
                "match_id": match.id,
                "unlocked": True,
                "already_unlocked": True,
                "credits_remaining": get_credit_balance(db, user_id),
            }

        # 4. Solo se pueden desbloquear negocios disponibles.
        if match.status != "available":
            raise HTTPException(
                status_code=409,
                detail="Este negocio no está disponible",
            )

        # 5. Consultar saldo.
        balance = get_credit_balance(db, user_id)

        if balance < 1:
            raise HTTPException(
                status_code=402,
                detail="No tienes créditos suficientes",
            )

        # 6. Registrar consumo.
        transaction = CreditTransactionModel(
            user_id=user_id,
            credits=-1,
            transaction_type="unlock",
            description="Desbloqueo de contacto de negocio",
            match_id=match.id,
        )

        db.add(transaction)

        # 7. Marcar coincidencia como desbloqueada.
        match.unlocked_at = datetime.now(timezone.utc)

        # 8. Confirmar ambas operaciones juntas.
        db.flush()

        remaining = get_credit_balance(db, user_id)

        db.commit()

        return {
            "match_id": match.id,
            "unlocked": True,
            "already_unlocked": False,
            "credits_remaining": remaining,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise
    

def get_credit_transactions(
    db: Session,
    user_id: uuid.UUID,
) -> list[CreditTransactionModel]:

    transactions = db.scalars(
        select(CreditTransactionModel)
        .where(CreditTransactionModel.user_id == user_id)
        .order_by(CreditTransactionModel.created_at.desc())
    ).all()

    return transactions

def get_pending_credit_purchases(
    db: Session,
):
    purchases = db.execute(
        select(
            CreditPurchaseModel,
            UserModel.full_name,
            UserModel.email,
        )
        .join(
            UserModel,
            UserModel.id == CreditPurchaseModel.user_id,
        )
        .where(
            CreditPurchaseModel.status == "pending_review"
        )
        .order_by(CreditPurchaseModel.created_at.asc())
    ).all()

    return purchases