from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal
import uuid


class AlternativeOfferCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=3000)
    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2,
    )
    source_name: str = Field(min_length=1, max_length=100)
    source_url: str | None = Field(default=None, max_length=1000)

    @field_validator("title", "source_name")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacio")
        return value

    @field_validator("description", "source_url")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class AlternativeOfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    title: str
    description: str | None
    price: Decimal | None
    source_name: str
    source_url: str | None
    availability_status: Literal[
        "pending_verification",
        "available",
        "unavailable",
        "unknown",
    ]
    verified_at: datetime | None
    created_at: datetime
