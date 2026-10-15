import uuid
from pydantic import BaseModel, ConfigDict,Field
from datetime import datetime


class RequestCreate(BaseModel):
    descripcion : str = Field(min_length=1, max_length = 200)
    categoria : str =Field(min_length=1, max_length=50)
    ciudad : str = Field(min_length=1, max_length=100)

class RequestResponse(BaseModel):
    id: uuid.UUID
    descripcion: str
    categoria: str
    ciudad: str
    created_at: datetime

model_config = ConfigDict(from_attributes=True)