"""add commercial response fields

Revision ID: 5ac8fc831be5
Revises: 590b05c69924
Create Date: 2026-10-22 17:21:52.984555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ac8fc831be5'
down_revision: Union[str, Sequence[str], None] = '590b05c69924'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(
        op.f('idx_businesses_location_geography'),
        table_name='businesses',
        postgresql_using='gist',
        postgresql_where='(location IS NOT NULL)',
    )

    op.add_column('request_business_matches', sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('request_business_matches', sa.Column('notes', sa.String(length=500), nullable=True))
    op.add_column('request_business_matches', sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True))

    # --- Datos existentes con coordenadas nulas ---
    # Opción A: rellenar con un valor por defecto (centro de Cuenca, Ecuador)
    op.execute("UPDATE requests SET latitud = -2.9001 WHERE latitud IS NULL")
    op.execute("UPDATE requests SET longitud = -79.0059 WHERE longitud IS NULL")

    # Opción B: eliminar las filas sin coordenadas (descomenta y quita la opción A).
    # Ojo: si otras tablas tienen FK hacia requests, bórralas primero o usa ON DELETE CASCADE.
    # op.execute("DELETE FROM requests WHERE latitud IS NULL OR longitud IS NULL")

    op.alter_column('requests', 'latitud',
                    existing_type=sa.DOUBLE_PRECISION(precision=53),
                    nullable=False)
    op.alter_column('requests', 'longitud',
                    existing_type=sa.DOUBLE_PRECISION(precision=53),
                    nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('requests', 'longitud',
                    existing_type=sa.DOUBLE_PRECISION(precision=53),
                    nullable=True)
    op.alter_column('requests', 'latitud',
                    existing_type=sa.DOUBLE_PRECISION(precision=53),
                    nullable=True)

    op.drop_column('request_business_matches', 'responded_at')
    op.drop_column('request_business_matches', 'notes')
    op.drop_column('request_business_matches', 'price')

    op.create_index(
        op.f('idx_businesses_location_geography'),
        'businesses',
        [sa.literal_column('(location::geography)')],
        unique=False,
        postgresql_using='gist',
        postgresql_where='(location IS NOT NULL)',
    )