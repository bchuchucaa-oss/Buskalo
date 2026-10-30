
from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from near_market.database import Base
from datetime import datetime
from geoalchemy2 import Geometry
import uuid
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
    Uuid,
    func,
)

from near_market.models.user import UserModel


class BusinessModel(Base):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    location = mapped_column(
    Geometry(geometry_type="POINT", srid=4326),
    nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    owner: Mapped[UserModel] = relationship(
        "UserModel",
        back_populates="businesses",
    )
    
    business_categories: Mapped[list["BusinessCategoryModel"]] = relationship(
    back_populates="business",
    cascade="all, delete-orphan",
    )

    matches: Mapped[list["RequestBusinessMatchModel"]] = relationship(
    "RequestBusinessMatchModel",
    back_populates="business",
    cascade="all, delete-orphan",
    )