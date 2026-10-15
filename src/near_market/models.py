
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from near_market.database import Base

class RequestModel(Base):
    __tablename__ = "requests"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    descripcion: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    categoria: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    ciudad: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )