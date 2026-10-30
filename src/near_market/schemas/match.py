import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field,AliasPath ,field_validator


class MatchRequestResponse(BaseModel):
    id: uuid.UUID
    descripcion: str

    category: str = Field(
        validation_alias=AliasPath("category", "name")
    )

    city: str = Field(
        validation_alias="ciudad"
    )

    model_config = ConfigDict(from_attributes=True)

class BusinessMatchCategoryResponse(BaseModel):
    id: uuid.UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class BusinessMatchBusinessResponse(BaseModel):
    id: uuid.UUID
    name: str
    city: str
    categories: list[BusinessMatchCategoryResponse] = Field(
        validation_alias="business_categories"
    )

    @field_validator("categories", mode="before")
    @classmethod
    def extract_categories(cls, value):
        return [item.category for item in value]

    model_config = ConfigDict(from_attributes=True)

class BusinessMatchResponse(BaseModel):
    id: uuid.UUID
    business: BusinessMatchBusinessResponse
    request: MatchRequestResponse
    distance_meters: float = Field(ge=0)
    status: str
    price: Decimal | None
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BusinessMatchesListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    matches: list[BusinessMatchResponse]