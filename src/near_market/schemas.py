import uuid
from pydantic import BaseModel,Field

class RequestCreate(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    descripcion : str = Field(min_length=1, max_length = 200)
    categoria : str =Field(min_length=1, max_length=50)
    ciudad : str = Field(min_length=1, max_length=100)