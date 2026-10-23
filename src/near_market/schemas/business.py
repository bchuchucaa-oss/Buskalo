
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

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
