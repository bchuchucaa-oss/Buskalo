from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from near_market.database import get_db
from near_market.websocket_manager import manager
from near_market.models import UserModel, BusinessModel
from near_market.services.auth import get_current_user
from near_market.services.security import (
    create_websocket_token,
)
import uuid
import jwt

from near_market.database import SessionLocal
from near_market.services.security import decode_websocket_token


router = APIRouter(prefix="/websocket", tags=["WebSocket"])


@router.post("/token")
def generate_websocket_token(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    business_id = db.scalar(
        select(BusinessModel.id)
        .where(BusinessModel.owner_id == current_user.id)
        .limit(1)
    )

    if business_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes negocios registrados",
        )

    token = create_websocket_token(str(current_user.id))

    return {
        "websocket_token": token,
        "token_type": "bearer",
        "expires_in": 120,
    }
    
def get_user_business_ids(user_id: uuid.UUID) -> list[uuid.UUID]:
    db = SessionLocal()

    try:
        user = db.get(UserModel, user_id)

        if user is None:
            return []

        statement = select(BusinessModel.id).where(
            BusinessModel.owner_id == user_id
        )

        return list(db.scalars(statement).all())

    finally:
        db.close()
        
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = decode_websocket_token(token)
        user_id = uuid.UUID(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        await websocket.close(code=1008)
        return

    business_ids = get_user_business_ids(user_id)

    if not business_ids:
        await websocket.close(code=1008)
        return

    connected_businesses = []

    try:
        for business_id in business_ids:
            await manager.connect(business_id, websocket)
            connected_businesses.append(business_id)

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        print("WebSocket desconectado por el cliente")

    finally:
        print("Ejecutando limpieza de conexiones")

        for business_id in connected_businesses:
            manager.disconnect(business_id, websocket)

        print("Conexiones eliminadas")