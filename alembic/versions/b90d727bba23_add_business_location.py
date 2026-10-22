
"""Add spatial location to businesses.

Revision ID: b90d727bba23
Revises: 1e32cc7578a7
"""

from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa


revision: str = "b90d727bba23"
down_revision: Union[str, Sequence[str], None] = "1e32cc7578a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the spatial column.
    op.add_column(
        "businesses",
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                spatial_index=False,
            ),
            nullable=True,
        ),
    )

    # Populate location from existing longitude and latitude.
    op.execute(
        """
        UPDATE businesses
        SET location = ST_SetSRID(
            ST_MakePoint(longitude, latitude),
            4326
        )
        WHERE longitude IS NOT NULL
          AND latitude IS NOT NULL
        """
    )

    # Create the spatial index exactly once.
    op.create_index(
        "idx_businesses_location",
        "businesses",
        ["location"],
        unique=False,
        postgresql_using="gist",
    )


def downgrade() -> None:
    # Remove only objects created by this migration.
    op.drop_index(
        "idx_businesses_location",
        table_name="businesses",
    )
    op.drop_column("businesses", "location")
