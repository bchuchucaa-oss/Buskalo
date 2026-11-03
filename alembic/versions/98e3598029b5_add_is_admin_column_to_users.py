"""add is_admin column to users

Revision ID: 98e3598029b5
Revises: d7186fc20121
Create Date: 2026-10-31 14:33:35.571530

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98e3598029b5'
down_revision: Union[str, Sequence[str], None] = 'd7186fc20121'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_admin",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")