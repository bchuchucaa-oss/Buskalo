from fastapi import FastAPI,HTTPException,Response,status
from src.near_market.requests import validate_request_description
from src.near_market.schemas import RequestCreate
import json
from uuid import UUID
from functools import reduce


app = FastAPI()

list_requests = []

@app.get('/health')
def health_comprobation():
    return {"status": "ok"}

@app.post('/requests')
def request(request: RequestCreate,response:Response):
    validacion = (
    validate_request_description(request.descripcion) 
    and validate_request_description(request.categoria) 
    and validate_request_description(request.ciudad) 
    )
    if validacion:
      list_requests.append(request)
      response.status_code= status.HTTP_201_CREATED
      return request
    else:
      raise HTTPException(status_code=422,detail='Descripcion invalida')

@app.get('/requests')
def requests_all():
   return list_requests

@app.get('/request/{request_id}')
def request_by_id(id:UUID,response:Response):
   result = next((req for req in list_requests if req.id == id), None)
   if result is None:
        raise HTTPException(status_code=404, detail="No encontrado")
   return result

@app.delete('/requests/{request_id}')
def delete_request(id:UUID,response: Response):
   global list_requests
   new_list_request = [req for req in list_requests if req.id != id]
   # Opcional: verificar si el elemento existía
   if len(new_list_request) == len(list_requests):
        raise HTTPException(status_code=404, detail="Request not found")
   list_requests = new_list_request
   response.status_code = status.HTTP_204_NO_CONTENT
   return {"status": "ok"}
   