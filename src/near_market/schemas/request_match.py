
from decimal import Decimal
from typing import Literal
import uuid
from pydantic import BaseModel, Field, field_validator

class RequestMatchResponse(BaseModel):
    business_id: uuid.UUID
    business_name: str
    distance_meters: float
    status: str

class MatchResponseCreate(BaseModel):
    status: Literal["available", "unavailable"]
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None