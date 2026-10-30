
from uuid import UUID
import uuid
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

class BusinessCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    address: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    category_ids: list[uuid.UUID] = Field(min_length=1, max_length=2)

    @field_validator("name", "city")
    @classmethod
    def reject_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío")
        return value

    @model_validator(mode="after")
    def coordinates_must_be_provided_together(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Debes proporcionar latitud y longitud juntas")
        return self
    

    @field_validator("category_ids")
    @classmethod
    def reject_duplicate_categories(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(value) != len(set(value)):
            raise ValueError("No puedes seleccionar categorías duplicadas")
        return value
 
class CategoryResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)



class BusinessResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    address: str | None
    city: str
    latitude: float | None
    longitude: float | None
    categories: list[CategoryResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_categories(cls, value):
        if isinstance(value, dict):
            return value

        return {
            "id": value.id,
            "name": value.name,
            "description": value.description,
            "address": value.address,
            "city": value.city,
            "latitude": value.latitude,
            "longitude": value.longitude,
            "categories": [
                association.category
                for association in value.business_categories
                if association.category is not None
            ],
        }


class BusinessUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    address: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    @field_validator("name", "city")
    @classmethod
    def reject_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío")
        return value


class NearbyBusinessResponse(BaseModel):
    business: BusinessResponse
    distance_meters: float = Field(ge=0)

