"""remove legacy requests without a real location

Revision ID: a18c6f29d3b1
Revises: 7f4a2c91d6e8
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a18c6f29d3b1"
down_revision: Union[str, Sequence[str], None] = "e56b5634ab68"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The earlier migration assigned this fallback point to legacy rows that
    # had no coordinates. Rows without a PostGIS point still lack a real location.
    op.execute(
        """
        DELETE FROM requests
        WHERE latitud = -2.9001
          AND longitud = -79.0059
          AND location IS NULL
        """
    )
    op.alter_column(
        "requests",
        "latitud",
        existing_type=sa.Float(),
        nullable=False,
    )
    op.alter_column(
        "requests",
        "longitud",
        existing_type=sa.Float(),
        nullable=False,
    )


def downgrade() -> None:
    # Deleted legacy requests cannot be reconstructed by a schema downgrade.
    pass
