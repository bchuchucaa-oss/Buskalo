
from decimal import Decimal
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RequestCreate(BaseModel):
    descripcion: str = Field(min_length=1, max_length=200)
    category_id: uuid.UUID
    ciudad: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    @field_validator("descripcion", "ciudad")
    @classmethod
    def reject_empty_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Este campo no puede estar vacio")

        return value


class RequestResponse(BaseModel):
    id: uuid.UUID
    descripcion: str
    category_id: uuid.UUID
    ciudad: str
    latitude: float = Field(validation_alias="latitud")
    longitude: float = Field(validation_alias="longitud")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BusinessRequestResponse(BaseModel):
    match_id: uuid.UUID
    request_id: uuid.UUID
    business_id: uuid.UUID
    business_name: str

    descripcion: str
    ciudad: str
    category_name: str

    status: str
    distance_meters: float
    price: Decimal | None
    notes: str | None
    created_at: datetime