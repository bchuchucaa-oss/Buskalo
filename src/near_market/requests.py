import uuid
from uuid import UUID
from near_market.schemas import RequestResponse, RequestCreate
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from near_market.models import RequestModel


list_requests = []
def validate_request_description(texto):  
    if not isinstance(texto, str):
        return False
    texto = texto.strip()
    if texto == "":
        return False
    if len(texto) > 200:
        return False
    return True

def validate_request_city(texto):
    if not isinstance(texto, str):
        return False
    texto = texto.strip()
    if texto == "":
        return False
    if len(texto) > 50:
        return False
    return True

def validate_request_category(texto):
    if not isinstance(texto, str):
        return False
    texto = texto.strip()
    if texto == "":
        return False
    if len(texto) > 100:
        return False
    return True

def create_identifier_request():
    identifier = uuid.uuid4()
    return identifier
#REUSE LATER
def get_all_requests(db:Session)->list[RequestModel]:
    statement = select(RequestModel).order_by(
        RequestModel.created_at.desc()
    )
    return list(db.scalars(statement).all())

def requests_by_id(db:Session,request_id:uuid.UUID)-> RequestModel:
    result = db.get(RequestModel,request_id)
    # result = next((req for req in list_requests if req.id == request_id), None)
    if result is None:
        raise HTTPException(status_code=404, detail="No encontrado")
    return result

def delete_by_id(request_id:uuid.UUID, db:Session)-> None:
    result = db.get(RequestModel, request_id)
    
    if result is None:
        raise HTTPException(status_code=404, detail="Request not found")

    db.delete(result)
    db.commit()

def create_request(db:Session, request: RequestCreate)-> RequestModel:
        #REVIEW VALIDATIONS OF CITY AND CATEGORY
        validacion = (
                validate_request_description(request.descripcion) 
                and validate_request_category(request.categoria) 
                and validate_request_city(request.ciudad) 
            )
        
        if validacion:  
            new_request = RequestModel(
                        id= uuid.uuid4(),
                        descripcion = request.descripcion,
                        categoria = request.categoria,
                        ciudad = request.ciudad
                    )
            db.add(new_request)
            db.commit()
            db.refresh(new_request)
            return new_request
        else:
            raise HTTPException(status_code=422,detail='Descripcion invalida')