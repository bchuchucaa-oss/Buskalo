
import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from near_market.database import get_db
from near_market.models import UserModel
from near_market.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from near_market.settings import settings


bearer_scheme = HTTPBearer(auto_error=False)


def register_user( email: str, password: str, full_name: str, db: Session = Depends(get_db)):
    normalized_email = email.strip().lower()

    existing_user = db.scalar(
        select(UserModel).where(UserModel.email == normalized_email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = UserModel(
        email=normalized_email,
        password_hash=hash_password(password),
        full_name=full_name.strip(),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    return user


def login_user(db: Session, email: str, password: str) -> str:
    normalized_email = email.strip().lower()

    user = db.scalar(
        select(UserModel).where(UserModel.email == normalized_email)
    )

    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return create_access_token(str(user.id))


def  get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise unauthorized

    user = db.get(UserModel, user_id)

    if user is None:
        raise unauthorized

    return user
