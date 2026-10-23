
from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from near_market.database import Base
import uuid
from sqlalchemy import (
    DateTime,
    String,
    Uuid,
    func,
)

# from near_market.models.business import BusinessModel
# from near_market.models.request import RequestModel

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    businesses: Mapped[list[BusinessModel]] = relationship(
        "BusinessModel",
        back_populates="owner",
    )

    requests: Mapped[list[RequestModel]] = relationship(
        "RequestModel",
        back_populates="user",
    )
