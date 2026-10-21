from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import FastAPI,Depends,HTTPException,Response,status
from near_market.requests import *
from near_market.schemas import RequestCreate,RequestResponse,BusinessCreate, BusinessResponse
from near_market.database import get_db
from near_market import businesses as business_service

from near_market import auth
from near_market.auth_schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from near_market.database import get_db
from near_market.models import UserModel


app = FastAPI()

@app.get('/health', status_code=status.HTTP_200_OK)
def health_comprobation():
    return {"status": "ok"}

@app.post('/requests',
          response_model= RequestResponse,
           status_code= status.HTTP_201_CREATED)
def request_create_endpont(request: RequestCreate,
                           db:Session = Depends(get_db),
                           current_user: UserModel = Depends(auth.get_current_user)):
    return create_request(db, request, user_id= current_user.id) 
 
@app.get('/requests', response_model= list[RequestResponse ], status_code=status.HTTP_200_OK)
def get_requests_all_endpoint(db:Session = Depends(get_db),
                               current_user: UserModel = Depends(auth.get_current_user)):
   response= get_all_requests(db, current_user)
   return response

@app.get('/requests/{request_id}',response_model=RequestResponse)
def request_by_id(request_id:UUID, 
                  db:Session = Depends(get_db), 
                  current_user: UserModel = Depends(auth.get_current_user)):
   result = requests_by_id(db, request_id, current_user)
   return result

@app.delete('/requests/{request_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
    request_id:UUID ,
    db: Session = Depends(get_db),
      current_user: UserModel = Depends(auth.get_current_user)):
   request_to_delete = request_by_id(db, request_id)
   if request_to_delete.user_id != current_user.id:
       raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes eliminar el requisito de otro usuario",
        )
   delete_by_id(request_id,db)

@app.post("/auth/register", status_code=201)
def register_user(data: UserCreate, db:Session = Depends(get_db)):
   return auth.register_user(db = db, 
                             email= str(data.email),
                             password= data.password,
                             full_name= data.full_name)

@app.post("/auth/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
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


@app.post(
    "/businesses",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_business_endpoint(
    business: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
):
    return business_service.create_business(
        db=db,
        business=business,
        owner_id=current_user.id,
    )


@app.get("/businesses", response_model=list[BusinessResponse])
def get_businesses(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
):
    return business_service.get_all_businesses(
        db=db,
        owner_id=current_user.id,
    )


@app.get("/businesses/{business_id}", response_model=BusinessResponse)
def get_business(
    business_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
):
    return business_service.get_business_by_id(
        db=db,
        business_id=business_id,
        owner_id=current_user.id,
    )


@app.put("/businesses/{business_id}", response_model=BusinessResponse)
def update_business_endpoint(
    business_id: UUID,
    business: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
):
    return business_service.update_business(
        db=db,
        business_id=business_id,
        owner_id=current_user.id,
        data=business,
    )


@app.delete("/businesses/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business_endpoint(
    business_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
):
    business_service.delete_business(
        db=db,
        business_id=business_id,
        owner_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
