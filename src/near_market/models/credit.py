
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import (
    Mapped,
    mapped_column, 
    relationship, 
    Session
    )
from near_market.database import Base

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Uuid,
    func,
    CheckConstraint,
    UniqueConstraint
)

class CreditPurchaseModel(Base):
    __tablename__ = "credit_purchases"

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_credit_purchase_amount_positive"),
        CheckConstraint("credits > 0", name="ck_credit_purchase_credits_positive"), 
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    package_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    credits: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending_review",
        server_default="pending_review",
        index=True,
    )

    payment_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    user = relationship(
        "UserModel",
        foreign_keys=[user_id],
        back_populates="credit_purchases",
    )

    reviewer = relationship(
        "UserModel",
        foreign_keys=[reviewed_by],
    )

    transactions = relationship(
        "CreditTransactionModel",
        back_populates="purchase",
    )


class CreditTransactionModel(Base):
    __tablename__ = "credit_transactions"

    __table_args__ = (
         CheckConstraint(
        """
        (
            transaction_type = 'purchase'
            AND credits > 0
            AND purchase_id IS NOT NULL
            AND match_id IS NULL
        )
        OR
        (
            transaction_type = 'unlock'
            AND credits < 0
            AND match_id IS NOT NULL
            AND purchase_id IS NULL
        )
        """,
        name="ck_credit_transaction_valid_operation",
        ),
        UniqueConstraint(
            "purchase_id",
            name="uq_credit_transaction_purchase",
        ),
        UniqueConstraint(
            "match_id",
            name="uq_credit_transaction_match",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    purchase_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("credit_purchases.id", ondelete="RESTRICT"),
        nullable=True,
    )

    # Positivo = créditos acreditados.
    # Negativo = créditos consumidos.
    credits: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("UserModel", back_populates="credit_transactions")

    purchase = relationship(
        "CreditPurchaseModel",
        back_populates="transactions",
    )
    
    match_id: Mapped[uuid.UUID | None] = mapped_column(
    Uuid(as_uuid=True),
    ForeignKey(
        "request_business_matches.id",
        ondelete="RESTRICT",
    ),
    nullable=True,
    )

