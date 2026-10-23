
from fastapi import FastAPI, Depends, status

from near_market.services import auth
from near_market.database import get_db
from near_market.models import UserModel
from near_market.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

from near_market.routers.requests import router as requests_router
from near_market.routers.business import router as businesses_router
from near_market.routers.request_matches import router as request_matches_router


app = FastAPI(title="NearMarket API")


# Routers principales
app.include_router(requests_router)
app.include_router(businesses_router)
app.include_router(request_matches_router)


@app.get("/health", status_code=status.HTTP_200_OK)
def health_comprobation():
    return {"status": "ok"}


# Autenticación
@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(
    data: UserCreate,
    db=Depends(get_db),
):
    return auth.register_user(
        db=db,
        email=str(data.email),
        password=data.password,
        full_name=data.full_name,
    )


@app.post("/auth/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db=Depends(get_db),
):
    token = auth.login_user(
        db=db,
        email=str(data.email),
        password=data.password,
    )

    return TokenResponse(access_token=token)


@app.get("/auth/me", response_model=UserResponse)
def get_me(
    current_user: UserModel = Depends(auth.get_current_user),
):
    return current_user
