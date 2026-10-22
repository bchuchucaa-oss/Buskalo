"""add request location

Revision ID: 55bc69aa7c98
Revises: 63d496cdf3c3
Create Date: 2026-10-21 13:36:36.315622

"""
from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55bc69aa7c98'
down_revision: Union[str, Sequence[str], None] = '63d496cdf3c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "requests",
        sa.Column("latitud", sa.Float(), nullable=True),
    )
    op.add_column(
        "requests",
        sa.Column("longitud", sa.Float(), nullable=True),
    )
    op.add_column(
        "requests",
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
            ),
            nullable=True,
        ),
    )

    op.create_index(
        "idx_requests_location",
        "requests",
        ["location"],
        unique=False,
        postgresql_using="gist",
    )


def downgrade() -> None:
    op.drop_index(
        "idx_requests_location",
        table_name="requests",
        postgresql_using="gist",
    )
    op.drop_column("requests", "location")
    op.drop_column("requests", "longitud")
    op.drop_column("requests", "latitud")