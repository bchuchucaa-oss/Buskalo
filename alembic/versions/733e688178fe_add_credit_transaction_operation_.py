"""add credit transaction operation constraint

Revision ID: 733e688178fe
Revises: b343e62d4d2e
Create Date: 2026-11-03 09:47:24.660374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '733e688178fe'
down_revision: Union[str, Sequence[str], None] = 'b343e62d4d2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.drop_constraint(
        "ck_credit_transaction_nonzero",
        "credit_transactions",
        type_="check",
    )

    op.create_check_constraint(
        "ck_credit_transaction_valid_operation",
        "credit_transactions",
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
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_credit_transaction_valid_operation",
        "credit_transactions",
        type_="check",
    )

    op.create_check_constraint(
        "ck_credit_transaction_nonzero",
        "credit_transactions",
        "credits != 0",
    )
