
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

class RequestModel(Base):
    __tablename__ = "requests"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    descripcion: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
    Uuid(as_uuid=True),
    ForeignKey("categories.id"),
    nullable=False,
    index=True,
    )

    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel",
    )

    ciudad: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    latitud: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    longitud: Mapped[float] = mapped_column(
            Float,
            nullable=False
        )

    location: Mapped[object | None] = mapped_column(
    Geometry(geometry_type="POINT", srid=4326),
    nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[UserModel | None] = relationship(
        "UserModel",
        back_populates="requests",
    )

    matches: Mapped[list["RequestBusinessMatchModel"]] = relationship(
        "RequestBusinessMatchModel",
        back_populates="request",
        cascade="all, delete-orphan",
    )