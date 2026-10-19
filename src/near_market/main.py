from fastapi import FastAPI,Depends,HTTPException,Response,status
from near_market.requests import *
from near_market.schemas import RequestCreate,RequestResponse
from near_market.database import get_db

from uuid import UUID


app = FastAPI()



@app.get('/health', status_code=status.HTTP_200_OK)
def health_comprobation():
    return {"status": "ok"}

@app.post('/requests',
          response_model= RequestResponse,
           status_code= status.HTTP_201_CREATED)
def request_create_endpont(request: RequestCreate,
                           db:Session = Depends(get_db)):
    return create_request(db, request)

@app.get('/requests', response_model= list[RequestResponse], status_code=status.HTTP_200_OK)
def get_requests_all_endpoint(db:Session = Depends(get_db)):
   response= get_all_requests(db)
   return response

@app.get('/requests/{request_id}',response_model=RequestResponse)
def request_by_id(request_id:UUID, db:Session = Depends(get_db)):
   result = requests_by_id(db, request_id)
   return result

@app.delete('/requests/{request_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id:UUID ,db: Session = Depends(get_db)):
   delete_by_id(request_id,db)
