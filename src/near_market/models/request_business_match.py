
from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from near_market.database import Base
from decimal import Decimal
from datetime import datetime
import uuid

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
    Uuid,
    func,
    UniqueConstraint,
    Numeric
)

class RequestBusinessMatchModel(Base):
    __tablename__ = "request_business_matches"

    __table_args__ = (
        UniqueConstraint(
            "request_id",
            "business_id",
            name="uq_request_business_match",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    request_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    distance_meters: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    request: Mapped["RequestModel"] = relationship(
        "RequestModel",
        back_populates="matches",
    )

    business: Mapped["BusinessModel"] = relationship(
        "BusinessModel",
        back_populates="matches",
    )
    unlocked_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    )