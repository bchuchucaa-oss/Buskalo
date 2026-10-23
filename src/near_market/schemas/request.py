
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class RequestCreate(BaseModel):
    descripcion: str = Field(min_length=1, max_length=200)
    categoria: str = Field(min_length=1, max_length=50)
    ciudad: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    @field_validator("descripcion", "categoria", "ciudad")
    @classmethod
    def reject_empty_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Este campo no puede estar vacio")

        return value


class RequestResponse(BaseModel):
    id: uuid.UUID
    descripcion: str
    categoria: str
    ciudad: str
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)