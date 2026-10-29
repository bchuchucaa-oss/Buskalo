from __future__ import annotations
import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from near_market.database import Base


class BusinessCategoryModel(Base):
    __tablename__ = "business_categories"

    __table_args__ = (
        UniqueConstraint(
            "business_id",
            "category_id",
            name="uq_business_category",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    business: Mapped["BusinessModel"] = relationship(
    back_populates="business_categories",
    )

    category: Mapped["CategoryModel"] = relationship(
        back_populates="business_categories",
    )
