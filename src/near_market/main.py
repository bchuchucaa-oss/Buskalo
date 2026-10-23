from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import FastAPI,Depends,HTTPException, Query,Response,status
from near_market.requests import *
from near_market.schemas.schema import MatchResponseCreate, NearbyBusinessResponse, RequestCreate, RequestMatchResponse,RequestResponse,BusinessCreate, BusinessResponse
from near_market.database import get_db
from near_market import businesses as business_service
from near_market.businesses import find_nearby_businesses
from near_market import auth
from near_market.auth_schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from near_market.database import get_db
from near_market.models.models import BusinessModel, UserModel
from near_market.models.models import RequestBusinessMatchModel


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
    new_request = create_request(db, request, user_id= current_user.id) 
    nearby_businesses = find_nearby_businesses(
        db=db,
        latitude=request.latitude,
        longitude=request.longitude,
        radius_meters=5000,
        limit=20,
    )

     # 3. Preparar las coincidencias
    matches = [
        RequestBusinessMatchModel(
            request_id=new_request.id,
            business_id=result["business"].id,
            distance_meters=result["distance_meters"],
            status="pending",
        )
        for result in nearby_businesses
    ]

    # 4. Guardar todas las coincidencias juntas
    if matches:
        db.add_all(matches)
        db.commit()

    return new_request
 
@app.get('/requests', response_model= list[RequestResponse ], status_code=status.HTTP_200_OK)
def get_requests_all_endpoint(db:Session = Depends(get_db),
                               current_user: UserModel = Depends(auth.get_current_user)):
   response= get_all_requests(db, current_user.id)
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

@app.get(
    "/businesses/nearby",
    response_model=list[NearbyBusinessResponse],
)
def get_nearby_businesses_endpoint(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    radius_meters: int = Query(default=5000, ge=1, le=50000),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    results = business_service.find_nearby_businesses(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius_meters,
        limit=limit,
    )

    return [
        {
            "business": result["business"],
            "distance_meters": result["distance_meters"],
        }
        for result in results
    ]


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


@app.get(
    "/requests/{request_id}/matches",
    response_model=list[RequestMatchResponse],
)
def get_request_matches(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
):
    # Verificar que la solicitud exista y pertenezca al usuario
    request_record = db.scalar(
        select(RequestModel).where(
            RequestModel.id == request_id,
            RequestModel.user_id == current_user.id,
        )
    )

    if request_record is None:
        raise HTTPException(
            status_code=404,
            detail="Solicitud no encontrada",
        )

    # Consultar las coincidencias y obtener el nombre del negocio
    results = db.execute(
        select(
            RequestBusinessMatchModel.business_id,
            BusinessModel.name.label("business_name"),
            RequestBusinessMatchModel.distance_meters,
            RequestBusinessMatchModel.status,
        )
        .join(
            BusinessModel,
            BusinessModel.id == RequestBusinessMatchModel.business_id,
        )
        .where(RequestBusinessMatchModel.request_id == request_id)
        .order_by(RequestBusinessMatchModel.distance_meters)
    ).all()

    return [
        RequestMatchResponse(
            business_id=row.business_id,
            business_name=row.business_name,
            distance_meters=row.distance_meters,
            status=row.status,
        )
        for row in results
    ]



@app.patch("/request-matches/{match_id}")
def update_match_response(
    match_id: uuid.UUID,
    payload: MatchResponseCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
):
    match = db.scalar(
        select(RequestBusinessMatchModel)
        .join(
            BusinessModel,
            BusinessModel.id == RequestBusinessMatchModel.business_id,
        )
        .where(
            RequestBusinessMatchModel.id == match_id,
            BusinessModel.owner_id == current_user.id,
        )
    )

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Coincidencia no encontrada",
        )

    if match.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Esta coincidencia ya fue respondida",
        )

    if payload.status == "available" and payload.price is None:
        raise HTTPException(
            status_code=422,
            detail="Debes indicar el precio cuando el producto o servicio está disponible",
        )

    match.status = payload.status
    match.price = payload.price
    match.notes = payload.notes
    match.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(match)

    return {
        "id": str(match.id),
        "status": match.status,
        "price": payload.price,
        "notes": payload.notes,
    }