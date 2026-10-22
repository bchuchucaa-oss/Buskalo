"""add geography index for nearby businesses

Revision ID: 63d496cdf3c3
Revises: b90d727bba23
Create Date: 2026-10-21 13:15:51.737349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63d496cdf3c3'
down_revision: Union[str, Sequence[str], None] = 'b90d727bba23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX idx_businesses_location_geography
        ON businesses
        USING GIST ((location::geography))
        WHERE location IS NOT NULL;
        """
    )
    op.create_index(
    "idx_requests_location",
    "requests",
    ["location"],
    unique=False,
    postgresql_using="gist",
)


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS idx_businesses_location_geography;
        """
    )
    pass


