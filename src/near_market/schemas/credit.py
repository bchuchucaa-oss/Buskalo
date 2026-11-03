
from datetime import datetime
from decimal import Decimal
from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict


class CreditPurchaseCreate(BaseModel):
    package_type: Literal["single", "pack_5"]


class CreditPurchaseResponse(BaseModel):
    id: uuid.UUID
    package_type: str
    amount: Decimal
    credits: int
    status: str
    payment_reference: str | None
    created_at: object

    model_config = ConfigDict(from_attributes=True)

class CreditTransactionResponse(BaseModel):
    id: uuid.UUID
    credits: int
    transaction_type: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
