
import uuid
from decimal import Decimal
from typing import Literal
from pydantic import (
    BaseModel,
    Field, 
    field_validator, 
    model_validator)

class RequestMatchResponse(BaseModel):
    match_id: uuid.UUID
    status: str
    price: Decimal | None
    city: str
    distance_range: str
    unlocked: bool

    business_name: str | None = None
    address: str | None = None
    phone: str | None = None
    whatsapp: str | None = None

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
    @model_validator(mode="after")
    def validate_price(self):
        if self.status == "available" and self.price is None:
            raise ValueError(
                "Debes indicar un precio cuando el servicio está disponible"
            )

        if self.status == "unavailable" and self.price is not None:
            raise ValueError(
                "No debes indicar un precio cuando el servicio no está disponible"
            )

        return self