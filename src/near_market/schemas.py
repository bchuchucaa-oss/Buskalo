
from typing import Literal
import uuid
from uuid import UUID
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


class BusinessCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    address: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @field_validator("name", "city")
    @classmethod
    def reject_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío")
        return value


class BusinessResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    address: str | None
    city: str
    latitude: float | None
    longitude: float | None
    model_config = ConfigDict(from_attributes=True)

class NearbyBusinessResponse(BaseModel):
    business: BusinessResponse
    distance_meters: float = Field(ge=0)

class RequestMatchResponse(BaseModel):
    business_id: uuid.UUID
    business_name: str
    distance_meters: float
    status: str

class MatchStatusUpdate(BaseModel):
    status: Literal["accepted", "rejected"]